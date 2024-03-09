import math
from rich import print
from PyNite import FEModel3D
# from PyNite.Visualization import render_model
import numpy as np

def grade_beam( mat: str,
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
                n_springs: float,
                UDL: list[float],
                pt_loads: list[tuple]
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
    model.add_material(mat, E, G, nu, rho)
    
    # Add nodes to the model
    dx = L / n_springs
    spring_stiffness = subgrade_modulus * w * dx
    print(f"{spring_stiffness = :0.2f}N/mm")
    x_chunks = np.linspace(0, L, n_springs+1)
    x_supports = list((x_chunks[:-1] + x_chunks[1:]) / 2)
    x_coords = [0.0] + x_supports + [L]
    nodes = []
    node_id = 0
    for x in x_coords:
        node_id += 1
        name = f"node{node_id}"
        nodes.append(name)
        model.add_node(name=name, X=x, Y=0.0, Z=0.0)
        if x in x_supports:
            model.def_support(name, 1, 0, 1, 1, 0, 0)
            model.def_support_spring(name, dof='DY', stiffness=spring_stiffness, direction='-') 

    # Add elements to the nodes
    model.add_member(name="M1", i_node="node1", j_node=name, material=mat, Iy=Iy, Iz=Iz, J=J, A=A)
    # Add a load combo
    model.add_load_combo(name="LC", factors={"LC": 1})
    # Add Distributed and Point loads
    model.add_member_dist_load(Member="M1", Direction="FY", w1=-UDL[0], w2=-UDL[1], x1=UDL[2], x2=UDL[3], case="LC") 
    for pt in pt_loads:
        model.add_member_pt_load(Member="M1", Direction="FY", P=-pt[0] , x=pt[1], case="LC")

    return model

def grade_beam_post_process(model: FEModel3D, L: float, n_springs: float, w:float) -> list[float]:
    """
    take the analyzed grade beam model and order the results to be displayed.
    specifically refers to the model defined in "grade_beam"
    it's assumed that the units are alway N and mm
    """
    A_dx = L/n_springs * w
    kPa = []
    x_sup = []
    for node_name, node in model.Nodes.items():
        if (node.X == 0.0) or (node.X == L):
            continue
        else:
            kPa.append(node.RxnFY["LC"]/A_dx*1000)
            x_sup.append(node.X)

    return kPa, x_sup
