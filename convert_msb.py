# Converts NEXXT (https://frankengraphics.itch.io/nexxt) metasprite banks to the format my edited version of the M1 disassembly uses.

import sys

with open(sys.argv[1], 'rb') as file:
    x_offset = int.from_bytes(file.read(1), 'little')
    y_offset = int.from_bytes(file.read(1), 'little')
    for ms_i in range(0x100):
        for sprite_i in range(0x40):
            y, tile, attrs, x = [int.from_bytes(file.read(1), 'little') for _ in range(4)]
            if (y, tile, attrs, x) == (0xFF, 0xFF, 0xFF, 0xFF):
                if sprite_i > 0:
                    print('    .byte $80\n')
                file.read((0x3F-sprite_i)*4)
                break
            if sprite_i == 0:
                print(f'Frame{ms_i:02X}:')
                print('    .byte $00,$00')
            print(f'    .byte ${(y-y_offset&0xFF):02X},${tile:02X},${attrs:02X},${(x-x_offset&0xFF):02X}')
