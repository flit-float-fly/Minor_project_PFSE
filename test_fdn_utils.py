import fdn_utils as fu
def test_convert_line_to_float():
    test_dict_1 = {"first": "1,2,3.9,4,5",
                 "second": "10,0.2,12.6"}
    test_dict_2 = {"third": "1,35.678,4,50",
                 "fourth": "tree,0.2,12.6"}
    assert fu.convert_line_to_float(test_dict_1) == {"first": [1,2,3.9,4,5],
                                                    "second": [10,0.2,12.6]}
    assert fu.convert_line_to_float(test_dict_2) == "Please enter a valid list for fourth"