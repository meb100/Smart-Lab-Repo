feature_vector_dictionary = {}  # {1: 7}   {index: count}

def extract_from_block(block):
    global feature_vector_dictionary
    
    feature_vector_dictionary.clear()
    for row in block:
        for pixel in row:
            binColorsUpdate(pixel)

def binColorsUpdate(pixel):
    global feature_vector_dictionary

    BIN_SIZE = 16
    red_index = int(pixel[0] / BIN_SIZE)
    green_index = int(pixel[1] / BIN_SIZE)
    blue_index = int(pixel[2] / BIN_SIZE)
    
    key = BIN_SIZE*BIN_SIZE*red_index + BIN_SIZE*green_index + blue_index
    
    if key in feature_vector_dictionary:
        feature_vector_dictionary[key] += 1
    else:
        feature_vector_dictionary[key] = 1