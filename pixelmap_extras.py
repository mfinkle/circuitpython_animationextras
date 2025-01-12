from adafruit_led_animation.helper import PixelMap


def rectangular_lines(pixel_object, width, height, gridmap):
    """
    Generate a PixelMap of rectangular concentric lines arranged in a grid.
    :param pixel_object: pixel object
    :param width: width of grid
    :param height: height of grid
    :param gridmap: a function to map x and y coordinates to the grid
                    see vertical_strip_gridmap and horizontal_strip_gridmap
    :return: PixelMap
    """
    if len(pixel_object) < width * height:
        raise ValueError("number of pixels is less than width x height")

    # We collect the groups of pixels ion this mapping list of lists
    mapping = []

    # Add the horizontal lines from above and below the mid-point
    start = 0
    stop = width
    for y in range(height // 2):
        mapping.append([gridmap(x, y) for x in range(start, stop)] + [gridmap(x, height - 1 - y) for x in range(start, stop)])
        start += 1
        stop -= 1

    # Append the vertical lines from above and below the mid-point
    start = 0
    stop = height
    for x in range(width // 2):
        mapping[x] += [gridmap(x, y) for y in range(start, stop)] + [gridmap(width - 1 - x, y) for y in range(start, stop)]
        start += 1
        stop -= 1

    # Note: we've added the corners into the mapping groups twice and could remove them to be more efficient

    return PixelMap(pixel_object, mapping, individual_pixels=True)


def map_from_mask(pixel_object, bitmap, gridmap):
    """
    Generate a PixelMap of groups of pixels clustered by palette index in a bitmap.
    :param pixel_object: pixel object
    :param bitmap: bitmap image used to structure the mask
    :param gridmap: a function to map x and y coordinates to the grid
                        see vertical_strip_gridmap and horizontal_strip_gridmap
    :return: PixelMap
    """
    if len(pixel_object) < bitmap.width * bitmap.height:
        raise ValueError("number of pixels is less than width x height")

    # We collect the groups of pixels from the bitmap using the palette index as the group key
    mapping_dict = {}
    for x in range(0, bitmap.width):
        for y in range(0, bitmap.height):
            index = bitmap[x, y]
            if index in mapping_dict:
                mapping_dict[index].append(gridmap(x, y))
            else:
                mapping_dict[index] = [gridmap(x, y)]

    # Convert the dict to a list of list and sort by the palette key
    mapping = [val for key, val in sorted(mapping_dict.items())]

    return PixelMap(pixel_object, mapping, individual_pixels=True)
