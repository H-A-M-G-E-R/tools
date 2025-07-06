def convert_palette(idxs: list, fp):
    pal_file = open(fp, 'rb')
    converted_pal = []
    i = 0
    for idx in idxs:
        if i & 3 == 0:
            converted_pal += [0, 0, 0, 0]
        else:
            pal_file.seek(idx*3)
            converted_pal.append(int.from_bytes(pal_file.read(1), 'little'))
            converted_pal.append(int.from_bytes(pal_file.read(1), 'little'))
            converted_pal.append(int.from_bytes(pal_file.read(1), 'little'))
            converted_pal.append(255)
        i += 1
    pal_file.close()
    return converted_pal
