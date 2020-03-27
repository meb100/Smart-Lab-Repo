
feature_vector = [0, 0, 0]
non_background_pixels = 0

# Input: "1,2,3/1,2,3/1,2,3-1,2,3/1,2,3/1,2,3"
# Input: [{"Data": "1,2,3/1,2,3/1,2,3-1,2,3/1,2,3/1,2,3", "Description": 23}, ..., ...] - each block is a row
'''
def extract_from_block(block):
    global feature_vector
    global non_background_pixels

    rows_unsplit = block["Data"].split("-") # ["1,2,3/1,2,3/1,2,3", "1,2,3/1,2,3/1,2,3"], Each elt: "1,2,3/1,2,3/1,2,3"
    for row in rows_unsplit:
        image_rgb_as_strings = row.split("/")   # ["1, 2, 3", "1, 2, 3"] (single row) Each elt: "1, 2, 3"
        for col in image_rgb_as_strings:
            pixel_string = col.split(",")   # ["1", "2", "3"] (single row, col location) Each elt: "1"
            pixel = [int(pixel_string[0]), int(pixel_string[1]), int(pixel_string[2])]
            electrolyticColorsExtractor(pixel)
'''

def extract_from_block(block):
    for row in block:
        for pixel in row:
            electrolyticColorsExtractor(pixel)

def electrolyticColorsExtractor(pixel):
    global feature_vector
    global non_background_pixels

    if not backgroundGreenColor(pixel):  # background subtraction
        non_background_pixels += 1
        if electrolyticBlackColor(pixel):
            feature_vector[0] += 1
        if ceramicColor(pixel):
            feature_vector[1] += 1
        if resistorTan(pixel):
            feature_vector[2] += 1

def backgroundGreenColor(color):
    return abs(color[0] - color[1]) < 25 and abs(color[1] - color[2]) < 25 and color[0] > 50 and color[1] > 50 and \
           color[2] > 50

def electrolyticBlackColor(color):
    return abs(color[0] - color[1]) < 15 and abs(color[1] - color[2]) < 15 and color[0] < 50 and color[1] < 50 and \
           color[2] < 50

def ceramicColor(color):
    return color[0] - color[1] > 25 and color[0] - color[1] < 70 and abs(color[1] - color[2]) < 15 and color[0] < 100

def resistorTan(color):
    return color[0] - color[1] > 25 and color[0] - color[1] < 60 and abs(color[1] - color[2]) < 15 and color[0] > 100

def normalize_feature_vector():
    global feature_vector
    for n in range(len(feature_vector)):
       feature_vector[n]  = float(feature_vector[n]) / float(non_background_pixels)