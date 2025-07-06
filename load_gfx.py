import romfile

def load_gfx(rom, idxs, gfx_info_tbl=0x786e0):
    gfx = [0]*0x2000
    for idx in idxs:
        rom.seek(gfx_info_tbl+idx*7)
        gfx_ptr = rom.read_int(1)*0x10000+rom.read_int(2)
        ppu_ptr = rom.read_int(2)
        size = rom.read_int(2)

        rom.seek(gfx_ptr)
        gfx[ppu_ptr^0x1000:(ppu_ptr^0x1000)+size] = [rom.read_int(1) for _ in range(size)]
    return gfx
