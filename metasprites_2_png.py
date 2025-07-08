import numpy as np
from PIL import Image
import romfile, palette, load_gfx
from twobpp import add_to_canvas_from_spritemap, bounding_box, to_image, convert_tile_from_bitplanes

def convert_metasprite(frame_ptr, place_tbl_ptr):
    signed = lambda n: (n & 0xFF) - 0x100 if (n & 0xFF) >= 0x80 else (n & 0xFF)

    metasprite = []
    frame_idx = 3
    place_idx = 0
    x_offset = 0
    y_offset = 0

    rom.seek(frame_ptr)
    init_cntrl = rom.read_int(1)
    metasprite_h_flip = init_cntrl & 0x40 == 0x40
    metasprite_v_flip = init_cntrl & 0x80 == 0x80
    cntrl = (init_cntrl >> 4) & 3
    cntrl = (init_cntrl & 0xC0) | 0x20 | cntrl
    place_num = init_cntrl & 0xF

    #y_radius = rom.read_int(1)
    #x_radius = rom.read_int(1)

    rom.seek(place_tbl_ptr+place_num*2)
    place_ptr = (place_tbl_ptr&0xFF0000)+rom.read_int(2)

    while True:
        rom.seek(frame_ptr+frame_idx)
        command = rom.read_int(1)
        frame_idx += 1
        if command == 0xFC:
            y_offset += rom.read_int(1)
            x_offset += rom.read_int(1)
            frame_idx += 2
        elif command == 0xFD:
            cntrl = rom.read_int(1)
            frame_idx += 1
        elif command == 0xFE:
            place_idx += 1
        elif command == 0xFF:
            break
        else:
            rom.seek(place_ptr+place_idx*2)
            y = rom.read_int(1)
            x = rom.read_int(1)
            if y & 0xF0 == 0x80:
                rom.read(10)
                y = rom.read_int(1)
                x = rom.read_int(1)
            if metasprite_h_flip:
                sprite_x = signed(x_offset - x - 8)
            else:
                sprite_x = signed(x_offset + x)
            if metasprite_v_flip:
                sprite_y = signed(y_offset - y - 8)
            else:
                sprite_y = signed(y_offset + y)
            metasprite.append({
                'x': sprite_x,
                'y': sprite_y,
                'tile': command,
                'palette': cntrl & 0x3,
                'bg_priority': cntrl & 0x20 == 0x20,
                'h_flip': cntrl & 0x40 == 0x40,
                'v_flip': cntrl & 0x80 == 0x80
            })
            place_idx += 1

    return metasprite

rom = romfile.ROMFile('M1.nes')

area_data = [
    (
        'brinstar',
        0x10000,
        [0x0F, 0x16, 0x19, 0x27, 0x0F, 0x12, 0x30, 0x21, 0x0F, 0x27, 0x2A, 0x3C, 0x0F, 0x15, 0x21, 0x38],
        [0x00, 0x14, 0x17, 0x18, 0x19, 0x16, 0x03, 0x04, 0x05, 0x06, 0x19, 0x16],
        0x97
    ),
    (
        'norfair',
        0x20000,
        [0x0F, 0x16, 0x19, 0x27, 0x0F, 0x12, 0x30, 0x21, 0x0F, 0x14, 0x23, 0x2C, 0x0F, 0x16, 0x24, 0x37],
        [0x00, 0x14, 0x17, 0x18, 0x19, 0x16, 0x04, 0x05, 0x07, 0x08, 0x09, 0x19, 0x16],
        0x8A
    ),
    (
        'tourian',
        0x30000,
        [0x0F, 0x16, 0x19, 0x27, 0x0F, 0x12, 0x30, 0x21, 0x0F, 0x27, 0x16, 0x30, 0x0F, 0x16, 0x2A, 0x37],
        [0x00, 0x14, 0x17, 0x18, 0x19, 0x16, 0x05, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x1A, 0x1C, 0x19, 0x16],
        0x8A
    ),
    (
        'kraid',
        0x40000,
        [0x0F, 0x16, 0x19, 0x27, 0x0F, 0x12, 0x30, 0x21, 0x0F, 0x27, 0x1B, 0x36, 0x0F, 0x17, 0x22, 0x31],
        [0x00, 0x14, 0x17, 0x18, 0x19, 0x16, 0x04, 0x05, 0x0A, 0x0F, 0x10, 0x11, 0x19, 0x16],
        0x97
    ),
    (
        'ridley',
        0x50000,
        [0x0F, 0x16, 0x19, 0x27, 0x0F, 0x12, 0x30, 0x21, 0x0F, 0x14, 0x13, 0x29, 0x0F, 0x13, 0x15, 0x27],
        [0x00, 0x14, 0x17, 0x18, 0x19, 0x16, 0x04, 0x05, 0x0A, 0x12, 0x13, 0x19, 0x16],
        0x8A
    )
]

pal = palette.convert_palette(area_data[0][2], 'palette.pal')
gfx = load_gfx.load_gfx(rom, area_data[0][3])

for frame_num in range(0x6A):
    rom.seek(0x1860B+frame_num*2)
    ptr = 0x10000+rom.read_int(2)
    rom.seek(0x1860B+frame_num*2+2)
    if ptr != 0x10000+rom.read_int(2):
        metasprite = convert_metasprite(ptr, 0x186DF)
        canvas = {}
        add_to_canvas_from_spritemap(canvas, metasprite, gfx)
        width, height = bounding_box(canvas)
        image = to_image(canvas, -width, -height, width, height)
        image.putpalette(pal, 'RGBA')
        image.save(f'out/obj_pngs/{frame_num:02X}.png')

for area_name, bank, pal_idxs, gfx_idxs, num_frames in area_data:
    pal = palette.convert_palette(pal_idxs, 'palette.pal')
    gfx = load_gfx.load_gfx(rom, gfx_idxs)

    rom.seek(bank+0x95A0)
    frame_ptr_tbl = bank+rom.read_int(2)
    rom.seek(bank+0x95A4)
    place_ptr_tbl = bank+rom.read_int(2)
    for frame_num in range(num_frames):
        rom.seek(frame_ptr_tbl+frame_num*2)
        ptr = bank+rom.read_int(2)
        rom.seek(frame_ptr_tbl+frame_num*2+2)
        if ptr != bank+rom.read_int(2):
            metasprite = convert_metasprite(ptr, place_ptr_tbl)
            canvas = {}
            add_to_canvas_from_spritemap(canvas, metasprite, gfx)
            width, height = bounding_box(canvas)
            image = to_image(canvas, -width, -height, width, height)
            image.putpalette(pal, 'RGBA')
            image.save(f'out/en_pngs/{area_name}_{frame_num:02X}.png')
