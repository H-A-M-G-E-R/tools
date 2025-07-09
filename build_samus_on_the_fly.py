import romfile, palette, load_gfx
from metasprites_2_png import convert_tile_from_bitplanes, convert_metasprite
from twobpp import gfx_2_image
import numpy as np
from PIL import Image

def relocate_chr_tiles(gfx, idxs):
    new_gfx = []
    for i in idxs:
        new_gfx.extend(gfx[i*16+0x1000:i*16+0x1010])
    return new_gfx

def print_relocated_frame(frame_ptr, idxs, place_lbl, offset=0):
    rom.seek(frame_ptr)
    init_cntrl = rom.read_int(1)
    print('    .byte ', end='')
    if init_cntrl & 0x80:
        print('OAMDATA_VFLIP + ', end='')
    if init_cntrl & 0x40:
        print('OAMDATA_HFLIP + ', end='')
    print(f'(${(init_cntrl >> 4) & 3} << 4) + _id_{place_lbl}{init_cntrl & 0xF:01X}, ${rom.read_int(1):02X}, ${rom.read_int(1):02X}')

    while True:
        command = rom.read_int(1)
        if command <= 0xFB:
            command = idxs.index(command) + offset
        print(f'    .byte ${command:02X}', end='')
        if command == 0xFC:
            print(f', ${rom.read_int(1):02X}, ${rom.read_int(1):02X}')
        elif command == 0xFD:
            print(', ', end='')
            cntrl = rom.read_int(1)
            if cntrl & 0x20:
                print('OAMDATA_PRIORITY + ', end='')
            if cntrl & 0x80:
                print('OAMDATA_VFLIP + ', end='')
            if cntrl & 0x40:
                print('OAMDATA_HFLIP + ', end='')
            print(f'${cntrl & 3:01X}')
        elif command == 0xFF:
            print()
            break
        else:
            print()


samus_frames = [0x03, 0x04, 0x05, 0x07, 0x08, 0x0C, 0x0D, 0x0E, 0x10, 0x12, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x22, 0x2B, 0x30, 0x35, 0x38, 0x39, 0x40, 0x41, 0x42, 0x46, 0x47, 0x48]

'''
samus_groups = [
    [0x03, 0x04, 0x05], # run
    [0x07], # facing forward
    [0x08], # stand
    [0x0C, 0x0D, 0x0E], # run and fire
    [0x10], # jump
    [0x12], # jump and fire
    [0x17, 0x18, 0x19, 0x1A], # somersault
    [0x1B, 0x1C, 0x1D, 0x1E], # roll
    [0x22], # stand and fire
    [0x2B], # stand and point up
    [0x30], # stand, point up and fire
    [0x35], # die
    [0x38], # jump and point up
    [0x39], # jump, point up and fire
    [0x40, 0x41, 0x42], # run and point up
    [0x46, 0x47, 0x48] # run, point up and fire
]
'''

'''
samus_groups = [
    [0x03,0x04,0x05, 0x0C,0x0D,0x0E, 0x10, 0x12],
    [0x07, 0x17,0x18,0x19,0x1A, 0x1B,0x1C,0x1D,0x1E, 0x35],
    [0x08, 0x22, 0x2B, 0x30, 0x38, 0x39, 0x40,0x41,0x42, 0x46,0x47,0x48],
]
'''

samus_groups = [
    [0x03, 0x0C, 0x40, 0x46],
    [0x04, 0x0D],
    [0x05, 0x0E],
    [0x41, 0x42, 0x47, 0x48],
    [0x07, 0x35],
    [0x08, 0x22, 0x2B, 0x30],
    [0x10, 0x12, 0x38, 0x39],
    [0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E]
]

max_samus_tiles = 0x10

frame_ids_to_skip = [
    0x5A, # skree projectile
    0x5B, 0x5C, 0x5D, 0x5E, # unused
    0x65, 0x66 # statues
]

hud_tiles = [
    0x76, 0x7F, 0x3A, # EN..
    0x6E, # empty energy tank
    0x6F, # full energy tank
    0x58, 0x59, # TIME
    0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9 # digits
]

item_frames = [0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59]

selected_en_frames = [0x61, 0x62, 0x80, 0x81, 0x89]

rom = romfile.ROMFile('M1.nes')

pal = palette.convert_palette([0x0F, 0x16, 0x19, 0x27], 'palette.pal')
gfx = load_gfx.load_gfx(rom, [0x00, 0x14, 0x17, 0x18, 0x19, 0x16, 0x03, 0x04, 0x05, 0x06, 0x19, 0x16])

metasprites = {}
unique_frames = []
for frame_num in range(0x6A):
    rom.seek(0x1860B+frame_num*2)
    ptr = 0x10000+rom.read_int(2)
    rom.seek(0x1860B+frame_num*2+2)
    if ptr != 0x10000+rom.read_int(2):
        metasprites[frame_num] = convert_metasprite(ptr, 0x186DF)
        unique_frames.append(frame_num)

# Samus facing forward fix
metasprites[0x07][1] = {'x': 0, 'y': -16, 'tile': 10, 'palette': 0, 'bg_priority': True, 'h_flip': False, 'v_flip': False}

# Objects
used_obj_tiles = []
for frame_num in unique_frames:
    if frame_num not in samus_frames and frame_num not in frame_ids_to_skip and frame_num not in item_frames:
        for sprite in metasprites[frame_num]:
            if sprite['tile'] not in used_obj_tiles:
                used_obj_tiles.append(sprite['tile'])
used_obj_tiles.append(0x8A) # energy drop
used_obj_tiles.extend(hud_tiles)
used_obj_tiles.extend([0xFF]*6) # filler
for frame_num in item_frames:
    for sprite in metasprites[frame_num]:
        if sprite['tile'] not in used_obj_tiles:
            used_obj_tiles.append(sprite['tile'])
while len(used_obj_tiles) < 0x80-max_samus_tiles:
    used_obj_tiles.append(0xFF)

image = gfx_2_image(gfx, used_obj_tiles[0x40-max_samus_tiles:], 0x1000)
image.putpalette(pal, 'RGBA')
image.save('out/items.png')
chrfile = open('out/items.chr', 'wb')
chrfile.write(bytes(relocate_chr_tiles(gfx, used_obj_tiles[0x40-max_samus_tiles:])))

# Samus
used_samus_tiles = []
for group_i, group in enumerate(samus_groups):
    used_tiles = []
    for frame_num in group:
        for sprite in metasprites[frame_num]:
            if sprite['tile'] not in used_tiles:
                used_tiles.append(sprite['tile'])
    while len(used_tiles) < max_samus_tiles:
        used_tiles.append(0xFF)
    used_samus_tiles.append(used_tiles)

for group_i, used_tiles in enumerate(used_samus_tiles):
    image = gfx_2_image(gfx, used_tiles + used_obj_tiles[:0x40-max_samus_tiles], 0x1000)
    image.putpalette(pal, 'RGBA')
    image.save(f'out/samus_suit_{group_i}.png')
    chrfile = open(f'out/samus_suit_{group_i}.chr', 'wb')
    chrfile.write(bytes(relocate_chr_tiles(gfx, used_tiles + used_obj_tiles[:0x40-max_samus_tiles])))

pal = palette.convert_palette([0x0F, 0x15, 0x34, 0x17], 'palette.pal')
gfx = load_gfx.load_gfx(rom, [0x00, 0x1B, 0x14, 0x17, 0x18, 0x19, 0x16, 0x03, 0x04, 0x05, 0x06, 0x19, 0x16])
for group_i, used_tiles in enumerate(used_samus_tiles):
    image = gfx_2_image(gfx, used_tiles + used_obj_tiles[:0x40-max_samus_tiles], 0x1000)
    image.putpalette(pal, 'RGBA')
    image.save(f'out/samus_suitless_{group_i}.png')
    chrfile = open(f'out/samus_suitless_{group_i}.chr', 'wb')
    chrfile.write(bytes(relocate_chr_tiles(gfx, used_tiles + used_obj_tiles[:0x40-max_samus_tiles])))

for group_i, group in enumerate(samus_groups):
    for frame_num in group:
        rom.seek(0x1860B+frame_num*2)
        print(f'ObjFrame{frame_num:02X}:')
        print_relocated_frame(0x10000+rom.read_int(2), used_samus_tiles[group_i], 'ObjPlace')
        print()

for frame_num in unique_frames:
    if frame_num not in samus_frames and frame_num not in frame_ids_to_skip:
        rom.seek(0x1860B+frame_num*2)
        print(f'ObjFrame{frame_num:02X}:')
        print_relocated_frame(0x10000+rom.read_int(2), used_obj_tiles, 'ObjPlace', max_samus_tiles)
        print()

for frame_num in selected_en_frames:
    rom.seek(0x19de0+frame_num*2)
    print(f'EnFrame{frame_num:02X}:')
    print_relocated_frame(0x10000+rom.read_int(2), used_obj_tiles, 'EnPlace', max_samus_tiles)
    print()

for tile_num in [0x5E, 0x5F] + hud_tiles:
    print(f'${tile_num:02X} -> ${used_obj_tiles.index(tile_num)+max_samus_tiles:02X}')
