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

st.header("Concrete Gradebeam Supported on Springs")

beam_expander = st.expander(label="**Loading & Support Input for beam**")
with beam_expander:
    st.subheader("Input values for different types of loads")
    st.write("**#-- separate with commas --#**")
    UDL_txt = st.text_input("Define UDL: UDL_start, UDL_end, x_start, x_end (+ = down)",
                            value = "2, 15, 0, 10000")
    point_list = st.text_input("List of point loads (+ = down)",
                               value = "1000, 5200")
    point_loc_list = st.text_input("corresponding location(s) on beam (0 = left end)",
                                   value = "5000, 7500")
    subgrade_txt = st.text_input("Enter a list of subgrade moduli you would like to test",
                                  value="0.1, 1, 5")
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
    w = st.number_input("Beam Width (mm)", value=200)
    h = st.number_input("Beam Height (mm)", value=800)
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

#loop through differnt subgrade moduli
Fy_rxns_dict = {}
for mod in inputs["subgrade_mods"]:
    gb_model, nodes = fdn.grade_beam(**beam_ppts, 
                                      subgrade_modulus=mod, 
                                      n_springs=n_springs,
                                      UDL=inputs["UDL"], 
                                      pt_loads=point_list)
    gb_model.analyze() # Changes the model by performing the analysis and adding analysis results
    
    Fy_rxns = [] #populate reactions for each mod
    for node in nodes:
        Fy = round(gb_model.Nodes[node].RxnFY["LC"], 1)
        Fy_rxns.append(Fy)

    Fy_rxns_dict[mod] = Fy_rxns #update dict with corresponding reactions

# Create the graph of spring responses
fig = go.Figure()
x_loc = [gb_model.Nodes[i].X for i in nodes]
A_dx = L/(n_springs-1)*w
for mod, rxns in Fy_rxns_dict.items():
    fig.add_trace(go.Scatter(
                x=x_loc,
                y=rxns,
                mode='lines+markers',
                name=mod))

fig.layout.title.text = "Gradebeam on Springs Response to Loading"
fig.layout.xaxis.title = "Position Along Gradebeam"
fig.layout.yaxis.title = "Reaction at spring"

st.plotly_chart(fig)