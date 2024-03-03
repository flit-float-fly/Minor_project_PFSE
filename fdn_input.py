import math
from PyNite import FEModel3D
# from PyNite.Visualization import render_model
from rich import print
import pandas as pd
import matplotlib.pyplot as plt
import fdn_model as fdn
import streamlit as st
import plotly.graph_objects as go

st.header("Gradebeam Supported on Springs")
st.subheader("Keep units consistent")

# Ask the user to input a list of subgrade moduli for analysis
subgrade_txt = st.text_input("Enter a list of subgrade moduli you would like to test, separated by commas:")

# Convert the input string to a list of floats
try:
    subgrade_mod = [float(num.strip()) for num in subgrade_txt.split(",")]
    st.write("These are the subgrade moduli you would like to run through:", subgrade_mod)
except ValueError:
    st.write("Please enter a valid list of numbers separated by commas.")

# User to choose number of springs to be supporting the grade beam
n_springs = st.number_input("Enter the number of spring supports along length of beam", value=10)

# User can input material and beam properties in the sidebar 
st.sidebar.subheader("Input Parameters")
mat_name = st.sidebar.text_input("Input Material Name", value="Concrete")
L = st.sidebar.number_input("Beam Length", value=10000, format="%.2e")
w = st.sidebar.number_input("Beam Width", value=200, format="%.2e")
h = st.sidebar.number_input("Beam Height", value=800, format="%.2e")
E = st.sidebar.number_input("Elastic Modulus", value=24648, format="%.2e")
Iz = st.sidebar.number_input("Moment of Inertia (z)", value=w*h**3/12, format="%.2e")
Iy = st.sidebar.number_input("Moment of Inertia (y)", value=h*w**3/12, format="%.2e")
nu = st.sidebar.number_input("Poisson's Ratio", value=0.2, format="%.2e")
rho = st.sidebar.number_input("Material Specific Weight", value=1e-3, format="%.2e")
J = st.sidebar.number_input("Polar Moment of Inertia", value=1.0, format="%.2e")

# build the beam_ppts that are 
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

# Run the simulations based on the list of subgrade moduli given
Fy_rxns_dict = {}
for mod in subgrade_mod:
    FBD_model, nodes = fdn.grade_beam(**beam_ppts, subgrade_modulus=mod, n_springs=n_springs)
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