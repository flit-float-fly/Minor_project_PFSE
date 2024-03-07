# Convert a string of values separated by commas to float
def convert_line_to_float(line: str) -> list[float]:
    try:
        line_converted_to_list = [float(num.strip()) for num in line.split(",")]
    except ValueError:
        st.write(f"Please enter a valid list for {name}")
