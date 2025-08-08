import romfile

unique_item_types = {
    0x00: 'ui_BOMBS',
    0x01: 'ui_HIGHJUMP',
    0x02: 'ui_LONGBEAM',
    0x03: 'ui_SCREWATTACK',
    0x04: 'ui_MARUMARI',
    0x05: 'ui_VARIA',
    0x06: 'ui_WAVEBEAM',
    0x07: 'ui_ICEBEAM',
    0x08: 'ui_ENERGYTANK',
    0x09: 'ui_MISSILES',
    0x0A: 'ui_MISSILEDOOR',
    0x0E: 'ui_MOTHERBRAIN',
    0x0F: 'ui_ZEBETITE1',
    0x10: 'ui_ZEBETITE2',
    0x11: 'ui_ZEBETITE3',
    0x12: 'ui_ZEBETITE4',
    0x13: 'ui_ZEBETITE5',
}

rom = romfile.ROMFile('M1.nes')
rom = romfile.ROMFile('Junkoid (1.1).nes')

rom.seek(0x09029) # ItemData
while rom.tell() < 0x0909F:
    word = rom.read_int(2)
    t = word >> 10
    x = (word >> 5) & 0x1F
    y = word & 0x1F
    if t in unique_item_types:
        s = unique_item_types[t]
    else:
        s = f'${t:02X}'
    print(f'    .word {s}{' '*(14-len(s))} + (${x:02X} << 5) + ${y:02X}')
