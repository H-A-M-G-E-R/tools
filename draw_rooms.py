import romfile, subprocess

def extract_macros(addr, n):
    macros = []
    rom.seek(addr)
    for i in range(n):
        macros.append((rom.read_int(1), rom.read_int(1), rom.read_int(1), rom.read_int(1)))
    return macros

def extract_structs(addr, n):
    structs = []
    for i in range(n):
        struct = []
        rom.seek(addr+i*2)
        rom.seek((addr&0xFF0000)+rom.read_int(2))

        while True:
            n = rom.read_int(1)
            if n == 0xFF:
                break
            struct.append([n >> 4] + [rom.read_int(1) for _ in range(0x10 if n & 0xF == 0 else n & 0xF)])

        structs.append(struct)

    return structs

def draw_room(addr, macros, structs):
    rom.seek(addr)
    room_pal = rom.read_int(1)

    nametable = [0xFF]*0x3C0
    attrs = [room_pal]*0x100

    while True:
        pos = rom.read_int(1)
        if pos == 0xFD or pos == 0xFF:
            break
        elif pos == 0xFE:
            continue
        x_pos = pos & 0xF
        y_pos = pos >> 4
        struct_i = rom.read_int(1)
        pal = rom.read_int(1)

        for row in structs[struct_i]:
            if y_pos >= 0xF:
                break
            x = x_pos + row[0]
            if x < 0x10:
                for macro_i in row[1:]:
                    c = x*2+y_pos*0x40
                    nametable[c] = macros[macro_i][0]
                    nametable[c+1] = macros[macro_i][1]
                    nametable[c+0x20] = macros[macro_i][2]
                    nametable[c+0x21] = macros[macro_i][3]
                    if pal != room_pal:
                        attrs[x+y_pos*0x10] = pal
                    x += 1
                    if x >= 0x10:
                        break
            y_pos += 1

    converted_attrs = []
    for y in range(0, 0x10, 2):
        for x in range(0, 0x10, 2):
            c = x+y*0x10
            converted_attrs.append(attrs[c]|(attrs[c+1]<<2)|(attrs[c+0x10]<<4)|(attrs[c+0x11]<<6))

    return bytearray(nametable+converted_attrs)

rom = romfile.ROMFile('M1.nes')

area_data = [
    ('brinstar', 0x10000, 0x32, 0x2F),
    ('norfair', 0x20000, 0x31, 0x2E),
    ('tourian', 0x30000, 0x20, 0x15),
    ('kraid', 0x40000, 0x27, 0x25),
    ('ridley', 0x50000, 0x1D, 0x2A),
]

for area_name, bank, num_structs, num_rooms in area_data:
    rom.seek(bank+0x959E)
    macros = extract_macros(bank+rom.read_int(2), 0x40)

    rom.seek(bank+0x959C)
    structs = extract_structs(bank+rom.read_int(2), num_structs)

    rom.seek(bank+0x959A)
    room_ptr_tbl = bank+rom.read_int(2)

    for i in range(num_rooms):
        rom.seek(room_ptr_tbl+i*2)
        out = open(f'out/rooms/{area_name}/{i:02X}.bin', 'wb')
        out.write(draw_room(bank+rom.read_int(2), macros, structs))
        out.close()
        subprocess.run(f"./lzsa -f 1 -r out/rooms/{area_name}/{i:02X}.bin out/rooms/{area_name}/lzsa1/{i:02X}_lzsa1.bin", shell=True)
        subprocess.run(f"./lzsa -f 2 -r out/rooms/{area_name}/{i:02X}.bin out/rooms/{area_name}/lzsa2/{i:02X}_lzsa2.bin", shell=True)
