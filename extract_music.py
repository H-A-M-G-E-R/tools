import romfile

def header_2_asm(note_len_tbl, repeat, tri_len, sq1_vol_ctrl, sq2_vol_ctrl):
    if note_len_tbl == 0:
        note_len_tbl_first = 4
    elif note_len_tbl == 0xB:
        note_len_tbl_first = 6
    elif note_len_tbl == 0x17:
        note_len_tbl_first = 7
    return f'    SongHeader NoteLengthsTbl@{note_len_tbl_first}, ${repeat:02X}, ${tri_len:02X}, ${sq1_vol_ctrl:02X}, ${sq2_vol_ctrl:02X}\n'

def track_2_asm(ptr, note_len_tbl, len_limit=None, end=False, noise=False):
    rom.seek(ptr)
    asm = ''
    note_len = 0
    track_len = 0
    in_loop = False
    len_in_loop = 0
    num_repeats = 0
    while True:
        if in_loop:
            asm += '    '
        cmd = rom.read_int(1)
        if cmd == 0:
            if in_loop:
                # in case the song ends while in a loop...
                track_len += len_in_loop
                if len_limit != None and track_len >= len_limit:
                    break
            asm += '    SongEnd\n'
            break
        elif cmd == 0xFF:
            asm += 'SongRepeat\n'
            in_loop = False
            track_len += len_in_loop*num_repeats
            if len_limit != None and track_len >= len_limit:
                break
        elif cmd >= 0xB0 and cmd < 0xC0:
            asm += f'    SongNoteLength ${cmd-0xB0:01X}\n'
            note_len = note_len_tbl[cmd-0xB0]
        elif cmd >= 0xC0:
            num_repeats = cmd-0xC0
            asm += f'    SongRepeatSetup ${num_repeats:01X}\n'
            if num_repeats == 0:
                num_repeats = 0xFF
            if in_loop:
                # if somehow that happens...
                track_len += len_in_loop
                if len_limit != None and track_len >= len_limit:
                    break
            in_loop = True
            len_in_loop = 0
        else:
            if cmd == 2:
                asm += '    SongRest\n'
            elif noise:
                name = None
                if cmd == 1:
                    name = 'DrumBeat00SFXData'
                elif cmd == 4:
                    name = 'DrumBeat01SFXData'
                elif cmd == 7:
                    name = 'DrumBeat02SFXData'
                elif cmd == 0xA:
                    name = 'DrumBeat03SFXData'
                if name != None:
                    asm += f'    .byte <{name}\n'
                else:
                    asm += f'    .byte ${cmd:02X}\n'
            elif cmd >= 0x80:
                asm += f'    .byte ${cmd:02X}\n'
            else:
                if cmd == 4 or cmd == 6:
                    cmd -= 2
                elif cmd == 0x7E:
                    cmd == 0x82
                note = cmd//2%12
                octave = cmd//24+2
                asm += f'    SongNote "{('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')[note]}{octave}"\n'
            if in_loop:
                len_in_loop += note_len
            else:
                track_len += note_len
                if len_limit != None and track_len >= len_limit:
                    break
    if end:
        asm += '    SongEnd\n'
    return asm, track_len

rom = romfile.ROMFile('M1.nes')

for bank in range(0, 0x60000, 0x10000):
    for song_i in range(12):
        rom.seek(bank+0xBBFA+song_i) # InitMusicIndexTbl

        rom.seek(bank+0xBD31+rom.read_int(1)) # SongHeaders
        note_len_tbl_idx, repeat, tri_len, sq1_vol_ctrl, sq2_vol_ctrl = [rom.read_int(1) for _ in range(5)]
        sq1, sq2, tri, noise = [rom.read_int(2) for _ in range(4)]

        rom.seek(bank+0xBEF7+note_len_tbl_idx) # NoteLengthsTbl
        note_len_tbl = [rom.read_int(1) for _ in range(0x10)]

        if sq1 >= 0x8000 or sq2 >= 0x8000 or tri >= 0x8000 or noise >= 0x8000:
            with open(f'out/songs/{bank//0x10000}_{song_i:X}.asm', 'w') as out_file:
                out = f'Song{bank//0x10000}_{song_i:X}Header:\n'
                out += header_2_asm(note_len_tbl_idx, repeat, tri_len, sq1_vol_ctrl, sq2_vol_ctrl)
                out += f'    .word '
                for channel_i, channel in enumerate((sq1, sq2, tri, noise)):
                    if channel < 0x8000:
                        out += f'${channel:04X}'
                    else:
                        out += f'@{('sq1', 'sq2', 'tri', 'noise')[channel_i]}'
                    out += '\n' if channel_i == 3 else ', '

                shortest_channel_i = None
                shortest_track_len = 99999
                for channel_i, channel in enumerate((sq1, sq2, tri, noise)):
                    if channel < 0x8000:
                        continue
                    _, track_len = track_2_asm(bank+channel, note_len_tbl)
                    if track_len < shortest_track_len:
                        shortest_channel_i = channel_i
                        shortest_track_len = track_len

                track_len = None
                if sq1 >= 0x8000:
                    asm, track_len = track_2_asm(bank+sq1, note_len_tbl, shortest_track_len, shortest_channel_i == 0)
                    out += '@sq1:\n' + asm + '\n'
                if sq2 >= 0x8000:
                    asm, track_len = track_2_asm(bank+sq2, note_len_tbl, shortest_track_len, shortest_channel_i == 1)
                    out += '@sq2:\n' + asm + '\n'
                if tri >= 0x8000:
                    asm, track_len = track_2_asm(bank+tri, note_len_tbl, shortest_track_len, shortest_channel_i == 2)
                    out += '@tri:\n' + asm + '\n'
                if noise >= 0x8000:
                    asm, track_len = track_2_asm(bank+noise, note_len_tbl, shortest_track_len, shortest_channel_i == 3, True)
                    out += '@noise:\n' + asm + '\n'

                out_file.write(out)
