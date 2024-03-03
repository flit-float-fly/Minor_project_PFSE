import math
from PyNite import FEModel3D
from PyNite.Visualization import render_model
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

beam_ppts = {   "name": mat_name,
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

# subgrade_mod = [4.8e-3, 16e-3, 1]  #N/mm3
# n_springs = 100
Fy_rxns_dict = {}

for mod in subgrade_mod:
    FBD_model, nodes = fdn.grade_beam(**beam_ppts, subgrade_modulus=mod, n_springs=n_springs) #send subgrade modulus; sand 4.8 - 16e-3 N/mm3
    FBD_model.analyze() # Changes the model by performing the analysis and adding analysis results
    # M_mid = round(FBD_model.Members['M1'].moment('Mz', 1500, 'LC3')/1e6, 1)
    # V_mid = round(FBD_model.Members['M1'].shear('Fy', 1500, 'LC3')/1e3, 1)
    # print(f"at {mod = }, {M_mid = }, {V_mid = }")
    # FBD_model.Members['M1'].plot_moment('Mz', combo_name='LC', n_points=300)
    # FBD_model.Members['M1'].plot_shear("Fy", combo_name='LC', n_points=300)
    
    Fy_rxns = []
    for node in nodes:
        Fy = round(FBD_model.Nodes[node].RxnFY["LC"], 1)
        Fy_rxns.append(Fy)

    Fy_rxns_dict[mod] = Fy_rxns
        
    # render_model(FBD_model, combo_name='LC3', annotation_size=50)

fig = go.Figure()

# Plot lines
fig.add_trace(
    go.Scatter(
    x=results["a"][1], 
    y=results["a"][0],
    line={"color": "red"},
    name="Column A"
    )
)
fig.add_trace(
    go.Scatter(
    x=results["b"][1], 
    y=results["b"][0],
    line={"color": "teal"},
    name="Column B"
    )
)

fig.add_trace(
    go.Scatter(
        y=[height_input],
        x=[factored_load_a],
        name="Example Calculation: Column A"
    )
)

fig.add_trace(
    go.Scatter(
        y=[height_input],
        x=[factored_load_b],
        name="Example Calculation: Column B"
    )
)

fig.layout.title.text = "Factored axial resistance of Column A and Column B"
fig.layout.xaxis.title = "Factored axial resistance, N"
fig.layout.yaxis.title = "Height of column, mm"


st.plotly_chart(fig)