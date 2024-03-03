import math
from rich import print
from PyNite import FEModel3D
from PyNite.Visualization import render_model
import numpy as np

def grade_beam( name: str,
                L: float,
                w: float,
                E: float,  
                A: float, 
                Iz: float, 
                Iy: float, 
                nu: float, 
                rho: float, 
                J: float, 
                subgrade_modulus: float,
                n_springs: float
              ) -> FEModel3D:
    """
    Build and return an FE Model to be analyzed and post-processed that represents a beam supported by n
    number of springs.
    - user defines total nbumber of springs
    - Subgrade modulus input in the form of force/volume ie: kN/m3 or lb/in3
    all other inputs are in this function.
    """
    #define shear modulus
    G = E/(2*(1+nu))

    model = FEModel3D() # Creates an empty model
    model.add_material(name, E, G, nu, rho)
    
    # Add nodes to the model
    dx = L / n_springs
    spring_stiffness = subgrade_modulus * w * dx
    print(f"{spring_stiffness = :0.2f}")
    x_coords = [i for i in np.linspace(0, L, n_springs)]
    nodes = []
    node_id = 0
    for coord_x in x_coords:
        node_id += 1
        name = f"node{node_id}"
        nodes.append(name)
        model.add_node(name=name, X=coord_x, Y=0.0, Z=0.0)
        model.def_support(name, 1, 0, 1, 1, 0, 0)
        model.def_support_spring(name, dof='DY', stiffness=spring_stiffness, direction='-') 

    # Add elements to the nodes
    model.add_member(name="M1", i_node="node1", j_node=name, material="Concrete", Iy=Iy, Iz=Iz, J=J, A=A)

    model.add_load_combo(name="LC", factors={"LC": 1})
    
    for mem in ["M1"]:
        model.add_member_pt_load(Member=mem, Direction="FY", P=12100 , x=250, case="LC")
        model.add_member_pt_load(Member=mem, Direction="MZ", P=11.9*0.75*1e6 , x=250, case="LC")
        model.add_member_pt_load(Member=mem, Direction="FY", P=-2200 , x=2750, case="LC")
        model.add_member_dist_load(Member=mem, Direction="FY", w1=-12.5, w2=-12.5, x1=0, x2=3000, case="LC") 
    
    return model, nodes