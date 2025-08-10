import romfile

signed_byte = lambda n: n if n <= 0x7F else n-0x100

rom = romfile.ROMFile('M1.nes')

area_data = [
    ('brinstar', 0x10000),
    ('norfair', 0x20000),
    ('tourian', 0x30000),
    ('kraid', 0x40000),
    ('ridley', 0x50000),
]

for area_name, bank in area_data:
    print(f'; {area_name}\n')

    y_accels = []
    rom.seek(bank+0x972B) # EnAccelYTable
    print('EnAccelYTable:')
    for i in range(0x14):
        signed_accel = signed_byte(rom.read_int(1))/4
        y_accels.append(signed_accel)
        print(f'    .byte {'-' if signed_accel < 0 else ' '}${round(abs(signed_accel)):02X} ; ${i:02X}')

    x_accels = []
    rom.seek(bank+0x973F) # EnAccelXTable
    print('EnAccelXTable:')
    for i in range(0x14):
        signed_accel = signed_byte(rom.read_int(1))/4
        x_accels.append(signed_accel)
        print(f'    .byte {'-' if signed_accel < 0 else ' '}${round(abs(signed_accel)):02X} ; ${i:02X}')

    rom.seek(bank+0x9753) # EnSpeedYTable
    print('EnSpeedYTable:')
    for i in range(0x14):
        signed_speed = (signed_byte(rom.read_int(1))+y_accels[i]/0x100)/2
        print(f'    .word {'-' if signed_speed < 0 else ' '}${round(abs(signed_speed*0x100)):04X} ; ${i:02X}')

    rom.seek(bank+0x9767) # EnSpeedXTable
    print('EnSpeedXTable:')
    for i in range(0x14):
        signed_speed = (signed_byte(rom.read_int(1))+x_accels[i]/0x100)/2
        print(f'    .word {'-' if signed_speed < 0 else ' '}${round(abs(signed_speed*0x100)):04X} ; ${i:02X}')
