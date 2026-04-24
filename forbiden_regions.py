

def read_floorplanfile(file): 
    width_heights = []
    x_y = []
    with open(file) as f:
        for line in f:
            if line.startswith("#") or not line.strip():  #line.strip() for empty lines
                continue
            t, width, height, x, y = line.split()
            if t == "MC1" or t == "NoC1" or t == "NoC2":
                width_heights.append((float(width), float(height)))
                x_y.append((float(x), float(y)))
    return width_heights, x_y

def read_padfile(file): 
    vdd = []
    gnd = []
    with open(file) as f:
        for line in f:
            if line.startswith("#") or not line.strip():  #line.strip() for empty lines
                continue
            t, x, y = line.split()
            if t == "V":
                vdd.append((int(x), int(y)))
            elif t == "G":
                gnd.append((int(x), int(y)))
    return vdd, gnd

def write_padfile(file, vdd, gnd):
    with open(file, "w") as f:
        for x, y in vdd:
            f.write(f"V\t{x}\t{y}\n")
        for x, y in gnd:
            f.write(f"G\t{x}\t{y}\n")


def forbidden_region(dim, pos):
    x_left = pos[0]
    x_right = dim[0] + pos[0]
    y_bottom = pos[1]
    y_top = dim[1] + pos[1]
    return x_left, x_right, y_bottom, y_top

def coordinate_to_virtual_grid(x1, x2, y1, y2):
    chip_width = 0.010764
    chip_height = 0.010764
    x_left = round((x1/chip_width)*72)
    x_right = round((x2/chip_width)*72)
    y_top = round((y2/chip_height)*72)
    y_bottom = round((y1/chip_height)*72)
    if(x_left > 72): 
        x_left = 72
    if(x_right > 72): 
        x_right = 72
    if(y_top > 72): 
        y_top = 72
    if(y_bottom > 72): 
        y_bottom = 72
    return x_left, x_right, y_bottom, y_top



dims, pos = read_floorplanfile("voltspot/example.flp")
forbidden_regions = []
for i in range(len(dims)):
    x1, x2, y1, y2, = forbidden_region(dims[i], pos[i])
    x_left, x_right, y_bottom, y_top = coordinate_to_virtual_grid(x1, x2, y1, y2)
    forbidden_regions.append((x_left, x_right, y_bottom, y_top))

vdd, gnd = read_padfile("voltspot/example.vgrid.padloc")

vdd_legal_sites = []
gnd_legal_sites = []

for pad in vdd:
    valid = True
    for region in forbidden_regions:
        if pad[0] >= region[0] and pad[0] <= region[1] and pad[1] >= region[2] and pad[1] <= region[3]:
            valid = False
            break
    if valid:
        vdd_legal_sites.append(pad)

for pad in gnd:
    valid = True
    for region in forbidden_regions:
        if pad[0] >= region[0] and pad[0] <= region[1] and pad[1] >= region[2] and pad[1] <= region[3]:
            valid = False
            break
    if valid:
        gnd_legal_sites.append(pad)

write_padfile("voltspot/legal_sites.vgrid.padloc", vdd_legal_sites, gnd_legal_sites)

