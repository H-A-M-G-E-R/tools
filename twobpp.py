import numpy as np
from PIL import Image

def gfx_2_image(gfx, idxs=None, offset=0):
    tiles = [convert_tile_from_bitplanes(gfx[i*0x10+offset:i*0x10+0x10+offset]) for i in (range(len(gfx)//0x10) if idxs == None else idxs)]
    while len(tiles) % 0x10 != 0:
        tiles.append(np.zeros((8, 8), dtype=np.uint8))
    rows = []
    for row_i in range(len(tiles)//0x10):
        rows.append(np.concatenate(tiles[row_i*0x10:row_i*0x10+0x10], 1))

    return Image.fromarray(np.concatenate(rows, 0), 'P')

''' Modified From SpriteSomething (https://github.com/Artheau/SpriteSomething) '''
def add_to_canvas_from_spritemap(canvas, tilemaps, graphics):
    # expects:
    #  a dictionary of spritemap entries
    #  a bytearray or list of bytes of 2bpp graphics

    for tilemap in reversed(tilemaps):
        x_offset = tilemap['x']
        y_offset = tilemap['y']
        index = tilemap['tile']
        palette = tilemap['palette']
        priority = tilemap['bg_priority']
        h_flip = tilemap['h_flip']
        v_flip = tilemap['v_flip']

        def draw_tile_to_canvas(new_x_offset, new_y_offset, new_index):
            tile_to_write = convert_tile_from_bitplanes(graphics[new_index*16+0x1000:new_index*16+0x1010])
            if h_flip:
                tile_to_write = np.fliplr(tile_to_write)
            if v_flip:
                tile_to_write = np.flipud(tile_to_write)
            for (i, j), value in np.ndenumerate(tile_to_write):
                if value != 0:  # if not transparent
                    canvas[(new_x_offset + j, new_y_offset + i)] = palette * 4 + int(value)

        draw_tile_to_canvas(x_offset, y_offset, index)

def bounding_box(canvas):
    '''Returns the minimum bounding box centered at the middle without cropping a single pixel'''
    if canvas.keys():
        x_min = min([x for (x, y) in canvas.keys()])
        x_max = max([x for (x, y) in canvas.keys()]) + 1
        y_min = min([y for (x, y) in canvas.keys()])
        y_max = max([y for (x, y) in canvas.keys()]) + 1

        return (max(abs(x_min), abs(x_max)), max(abs(y_min), abs(y_max)))
    else:
        return (0, 0)

def to_image(canvas, left, top, right, bottom):
    '''Returns an image cropped by a bounding box'''
    if canvas.keys():
        image = Image.new('P', (right-left, bottom-top), 0)

        pixels = image.load()

        for (i, j), value in canvas.items():
            pixels[(i-left, j-top)] = value
    else:  # the canvas is empty
        image = Image.new('P', (1, 1), 0)

    return image

def convert_tile_from_bitplanes(raw_tile):
    # See https://www.nesdev.org/wiki/PPU_pattern_tables for the format
    # an attempt to make this ugly process mildly efficient

    # axes 1 and 0 are the rows and columns of the image, respectively
    # numpy has the axes swapped
    tile = np.zeros((8, 1, 2), dtype=np.uint8)

    tile[:, 0, 0] = raw_tile[0:8] # bitplane 0
    tile[:, 0, 1] = raw_tile[8:16] # bitplane 1

    tile_bits = np.unpackbits(tile, axis=1, bitorder='big') # decompose the bitplanes to rows
    fixed_bits = np.packbits(tile_bits, axis=2, bitorder='little') # combine the bitplanes
    returnvalue = fixed_bits.reshape(8, 8)
    return returnvalue
