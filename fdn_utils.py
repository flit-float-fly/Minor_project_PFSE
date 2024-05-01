import planesections as ps

def convert_line_to_float(line_dict: dict) -> list[float]:
    """
    convert a dictionary of strings to a list of floats;
    the dict values should be numbers in the form of text
    separated by commas.
    """
    for name, line_text in line_dict.items():
        try:
            list_of_floats = [float(value.strip()) for value in line_text.split(",")]
            line_dict[name] = list_of_floats #overwrite dict with new values
        except ValueError:
            error_text = (f"Please enter a valid list for {name}")
            return error_text
        
    return line_dict

def visualize_beam(L: float, UDL: list[float], pts: list[float]):
    """
    Use plane sections library to display the beam showing loading arrangement.
    returns an EulerBeam model ready for plotting;
    note, this is not intended to be used for analysis.
    """
    # setup beam model
    beam = ps.newEulerBeam(L)

    # setup UDL
    beam.addLinLoadVertical(UDL[2], UDL[3], [-UDL[0], -UDL[1]])

    # setup point loads
    for i, pt in enumerate(pts):
        pt_mag, pt_x = pt
        beam.addVerticalLoad(pt_x, -pt_mag, label = i) #add neg b/c sign convention is opposite to input

    return beam