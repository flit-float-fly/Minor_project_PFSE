import math
from PyNite import FEModel3D
# from PyNite.Visualization import render_model
from rich import print
import pandas as pd
import matplotlib.pyplot as plt
import fdn_model as fdn
import streamlit as st
import plotly.graph_objects as go
# from eng_module.utils import convert_to_numeric

st.header("Gradebeam Supported on Springs")

beam_expander = st.expander(label="Input for beam")
with beam_expander:
    st.subheader("Input values for different types of loads, separate with commas")
    UDL_txt = st.text_input("Define UDL: UDL_start, UDL_end, x_start, x_end (+ = down)",
                            value = "10, 15, 0, 10000")
    point_list = st.text_input("List of point loads (+ = down)",
                               value = "1000, 5200")
    point_loc_list = st.text_input("corresponding location(s) on beam (0 = left end)",
                                   value = "5000, 7500")
    subgrade_txt = st.text_input("Enter a list of subgrade moduli you would like to test",
                                  value="0.1, 1, 5")

    # Convert the input strings to a list of floats
    inputs = {"UDL": UDL_txt, 
              "point_loads": point_list,
              "point_locations": point_loc_list,
              "subgrade_mods": subgrade_txt} 
    
    for name, values in inputs.items():
        try:
            input_converted = [float(num.strip()) for num in values.split(",")]
            # st.write(f"{name}:", input_converted)
            inputs[name] = input_converted #overwrite dict with new values
        except ValueError:
            st.write(f"Please enter a valid list for {name}")

# User to choose number of springs to be supporting the grade beam
n_springs = st.number_input("Enter the number of spring supports along length of beam", value=10)

# User can input material and beam properties in the sidebar 
st.sidebar.subheader("Member Parameters; Units = N,mm")
mat_name = st.sidebar.text_input("Input Material Name", value="Concrete")
L = st.sidebar.number_input("Beam Length (mm)", value=10000)
w = st.sidebar.number_input("Beam Width (mm)", value=200)
h = st.sidebar.number_input("Beam Height (mm)", value=800)
E = st.sidebar.number_input("Elastic Modulus (MPa)", value=24648)
Iz = st.sidebar.number_input("Moment of Inertia-z (mm4)", value=w*h**3/12)
Iy = st.sidebar.number_input("Moment of Inertia-y (mm4)", value=h*w**3/12)
nu = st.sidebar.number_input("Poisson's Ratio", value=0.2, format="%.2f")
rho = st.sidebar.number_input("Material Specific Weight (N/mm3)", value=1e-6, format="%.6e")
J = st.sidebar.number_input("Polar Moment of Inertia (mm3)", value=1.0)

# Create tuples from point loads and locations
point_list = list(zip(inputs["point_loads"], inputs["point_locations"]))

beam_ppts = {   "mat": mat_name,
                "L": L,
                "w": w,
                "E": E,
                "A": h*w, 
                "Iz": Iz,
                "Iy": Iy,
                "nu": nu, 
                "rho": rho,
                "J": J
            }

#loop through differnt subgrade moduli
Fy_rxns_dict = {}
for mod in inputs["subgrade_mods"]:
    FBD_model, nodes = fdn.grade_beam(**beam_ppts, subgrade_modulus=mod, n_springs=n_springs,
                                       UDL=inputs["UDL"], pt_loads=point_list)
    FBD_model.analyze() # Changes the model by performing the analysis and adding analysis results
    
    Fy_rxns = [] #populate reactions for each mod
    for node in nodes:
        Fy = round(FBD_model.Nodes[node].RxnFY["LC"], 1)
        Fy_rxns.append(Fy)

    Fy_rxns_dict[mod] = Fy_rxns #update dict with corresponding reactions

base_rxn_df = pd.DataFrame(Fy_rxns_dict)

# Show dataframe
# st.dataframe(base_rxn_df)

# Create the graph of spring responses
fig = go.Figure()

for col in base_rxn_df.columns:
    fig.add_trace(go.Scatter(
                x=base_rxn_df.index,
                y=base_rxn_df[col],
                mode='lines+markers',
                name=col)
                )

fig.layout.title.text = "Gradebeam on Springs Response to Loading"
fig.layout.xaxis.title = "Position Along Gradebeam"
fig.layout.yaxis.title = "Reaction at spring"

st.plotly_chart(fig)