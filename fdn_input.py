import math
from PyNite import FEModel3D
from rich import print
import pandas as pd
import matplotlib.pyplot as plt
import fdn_model as fdn
import streamlit as st
import plotly.graph_objects as go
import fdn_utils as fu
import planesections as ps

## TO DO:
# - 2 Columns in expander for point loads + Locs & 
# point moms + Locs
# - radio button to allow for cracked section
# - 2d plate analysis
# 

st.header("Concrete Gradebeam Supported on Springs")

beam_expander = st.expander(label="**Loading & Support Input for beam**")
with beam_expander:
    st.subheader("Input values for different types of loads")
    st.write("**#-- separate with commas --#**")
    UDL_txt = st.text_input("Define UDL: UDL_start, UDL_end, x_start, x_end (+ = down)",
                            value = "1, 1, 0, 10000")
    point_list = st.text_input("List of point loads (+ = down)",
                               value = "1000, 1000")
    point_loc_list = st.text_input("corresponding location(s) on beam (0 = left end)",
                                   value = "2500, 7500")
    subgrade_txt = st.text_input("Enter a list of subgrade moduli you would like to test",
                                  value="0.01, 0.1, 1")
    # User to choose number of springs to be supporting the grade beam
    n_springs = st.number_input("Enter the number of spring supports along length of beam", value=10)


    # Convert the input strings to a list of floats
    inputs = {"UDL": UDL_txt, 
              "point_loads": point_list,
              "point_locations": point_loc_list,
              "subgrade_mods": subgrade_txt} 
    
    inputs = fu.convert_line_to_float(inputs)

    # display error if function sends error message
    if type(inputs) == str:
        st.write(inputs)

# User can input material and beam properties in the sidebar 
input_sidebar = st.sidebar
with input_sidebar:
    st.subheader("Member Parameters; Units = N, mm")
    L = st.number_input("Beam Length (mm)", value=10000)
    w = st.number_input("Beam Width (mm)", value=1000)
    h = st.number_input("Beam Height (mm)", value=1000)
    fc = st.number_input("Conc. Strength (MPa)", value=30)
    E = st.number_input("Elastic Modulus (MPa)", value=4500*math.sqrt(fc))

    adv_exp = st.expander(label="Advanced Properties")
    with adv_exp:
        st.write("Assumes uncracked state as default")
        Iz = st.number_input("Moment of Inertia-z (mm4)", value=w*h**3/12)
        Iy = st.number_input("Moment of Inertia-y (mm4)", value=h*w**3/12)
        nu = st.number_input("Poisson's Ratio", value=0.2, format="%.2f")
        rho = st.number_input("Material Specific Weight (N/mm3)", value=1e-6, format="%.6e")
        J = st.number_input("Polar Moment of Inertia (mm3)", value=1.0)

# Create tuples from point loads and locations
point_list = list(zip(inputs["point_loads"], inputs["point_locations"]))

# Setup and plot beam visualization
beam = fu.visualize_beam(L, inputs["UDL"], point_list)
beam_image, ax = ps.plotBeamDiagram(beam, plotLabel=False, labelForce=True, plotForceValue=False)
st.pyplot(beam_image)

#compile properties for beam configuration
beam_ppts = {   "mat": "Concrete",
                "L": L,
                "w": w,
                "E": E,
                "A": h*w, 
                "Iz": Iz,
                "Iy": Iy,
                "nu": nu, 
                "rho": rho,
                "J": J}

#loop through different subgrade moduli; save to dict
Fy_rxns_dict = {}
for mod in inputs["subgrade_mods"]:
    gb_model = fdn.grade_beam(**beam_ppts, 
                                      subgrade_modulus=mod, 
                                      n_springs=n_springs,
                                      UDL=inputs["UDL"], 
                                      pt_loads=point_list)
    gb_model.analyze() # Changes the model by performing the analysis and adding analysis results
    rxn_kPa, x_sup = fdn.grade_beam_post_process(gb_model, L, n_springs, w)
    Fy_rxns_dict[mod] = rxn_kPa #update dict with corresponding pressures

# st.write(gb_model.Members["M1"].DistLoads)
# st.write(sum([gb_model.Nodes[i].RxnFY["LC"] for i in gb_model.Nodes]))
# st.write(Fy_rxns_dict)
    
# Create the graph of base response
fig = go.Figure()
for mod, kPas in Fy_rxns_dict.items():
    fig.add_trace(go.Scatter(
                x=x_sup,
                y=kPas,
                mode='lines+markers',
                name=mod))

fig.layout.title.text = "Gradebeam on Springs Response to Loading"
fig.layout.xaxis.title = "Position Along Gradebeam (mm)"
fig.layout.yaxis.title = "pressure under beam (kPa)"

st.plotly_chart(fig)