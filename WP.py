# WP-F: Walking Pads - Freezing algorithm

import subprocess
import math

# # to be configured manyally
# FLOORPLAN = "../new_floorplan/alpha_ev6/ev6.flp"
# PTRACE = "../new_floorplan/alpha_ev6/ev6_fixed.ptrace"
# CONFIGURATION = "../new_floorplan/alpha_ev6/ev6.config"
# LEGAL_PADLOC = "voltspot/ev6.vgrid.padloc"
# PAD_LOCATIONS = "voltspot/pads.vgrid.padloc"

# GRID_MAX = 158 # it is 72 for the example chip and 158 for the ev6 chip

FLOORPLAN     = "example.flp"
PTRACE        = "example.ptrace"
CONFIGURATION = "pdn.config"
LEGAL_PADLOC  = "voltspot/example.vgrid.padloc"
PAD_LOCATIONS = "voltspot/pads.vgrid.padloc"
GRID_MAX      = 72

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

def write_padfile(file, vdd, gnd): #for writing new C4 pad locations after each WP iteration
    with open(file, "w") as f:
        for x, y in vdd:
            f.write(f"V\t{x}\t{y}\n")
        for x, y in gnd:
            f.write(f"G\t{x}\t{y}\n")

def read_legal_padfile(file):
    legal_sites = []
    with open(file) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            t, x, y = line.split()
            if t == "V" or t == "G":
                legal_sites.append((int(x), int(y)))
            else:
                continue
    return legal_sites


def read_grid_ir(file):
    data = {}
    with open(file) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            x, y, val = line.split()
            data[(int(x), int(y))] = float(val)
    return data

def get_hotspot(grid):
    return max(grid.items(), key = lambda x: x[1])

  
def run_voltspot():
    subprocess.run([
        "./voltspot",
        "-f", FLOORPLAN,
        "-p", PTRACE,
        "-c", CONFIGURATION,
        "-PDN_padconfig", "0",
        "-padloc_file_in", "pads.vgrid.padloc",
        "-gridvol_file", "steady.gridIR"
    ], cwd="voltspot")

def find_neighbors_IR(x, y, IR): #grid is 73 by 73
    center = IR[(x, y)]
    if (x == 0):
        left = center
    else:
        left = IR[(x-1, y)]
    if (x == GRID_MAX):
        right = center
    else:
        right = IR[(x+1, y)]
    if (y == 0):
        bottom = center
    else:
        bottom = IR[(x, y-1)]
    if (y == GRID_MAX):
        top = center
    else:
        top = IR[(x, y+1)]
    return { "left":left,"right":right, "top":top, "bottom":bottom } 

# def neighbor_helper(x, y):
#     if x == 1:
#         left = 1
#     elif x == 0:
#         left = 0
#     else:
#         left = 2

#     if x == 71:
#         right = 1
#     elif x == GRID_MAX:
#         right = 0
#     else:
#         right = 2

#     if y == 1:
#         bottom = 1
#     elif y == 0:
#         bottom = 0
#     else: 
#         bottom = 2
    
#     if y == 71:
#         top = 1
#     elif y == GRID_MAX:
#         top = 0
#     else:
#         top = 2
#     return { "left":left,"right":right, "top":top, "bottom":bottom } 

# def find_two_neighbors_IR(x, y, IR): 
#     center = IR[(x, y)]
#     if x == 1:
#         left_IR = IR[(x-1, y)]
#     elif x == 0:
#         left_IR = center
#     else:
#         left_IR = (IR[(x-1, y)] + IR[(x-2, y)]) / 2

#     if x == 71:
#         right_IR = IR[(x+1, y)]
#     elif x == GRID_MAX:
#         right_IR = center
#     else: 
#         right_IR = (IR[(x+1, y)] + IR[(x+1, y)]) / 2

#     if y == 1:
#         bottom_IR = IR[(x, y-1)]
#     elif y == 0:
#         bottom_IR = center
#     else:
#         bottom_IR = (IR[(x, y-1)] + IR[(x, y-2)]) / 2

#     if y == 71:
#         top_IR = IR[(x, y+1)]
#     elif y == GRID_MAX:
#         top_IR = center
#     else: 
#         top_IR = (IR[(x, y+1)] + IR[(x, y+2)]) / 2

#     return { "left":left_IR,"right":right_IR, "top":top_IR, "bottom":bottom_IR } 
    
        


    

def compute_forces(data):
    force_x = data["right"] - data["left"]
    force_y = data["top"] - data["bottom"]
    return {"x":force_x, "y":force_y} # dictionary



def distance_from_forces(data, D):
    x_force = data["x"]
    y_force = data["y"]
    magnitude = math.hypot(x_force, y_force)
    if(magnitude < 1e-12):
        return {"x": 0, "y": 0}
    x_norm = x_force/magnitude
    y_norm = y_force/magnitude
    x_move = round(x_norm*D)
    y_move = round(y_norm*D)
    return {"x":x_move, "y":y_move}
    

def not_occupied(site, gnd, accepted_vdd, remaining_old_vdd):
    for g in gnd:
        if site == g:
            return False
    for v in accepted_vdd:
        if site == v:
            return False
    for v in remaining_old_vdd:
        if site == v:
            return False
    return True

def snap_to_legal_site(candidate, legal_sites, gnd, accepted_vdd, remaining_old_vdd):
    min_val = float("inf")
    current_site = None
    for site in legal_sites:
        dist = math.hypot(candidate[0]-site[0], candidate[1]-site[1])
        if dist < min_val and not_occupied(site, gnd, accepted_vdd, remaining_old_vdd):
            min_val = dist
            current_site = site
    return current_site

    



sim_length = 1000
D = 100 #update each iteration
freeze_rate = 0.99
legal_sites = read_legal_padfile(LEGAL_PADLOC)
for i in range(sim_length):
    run_voltspot()
    grid = read_grid_ir("voltspot/steady.gridIR") #use this as input to find_neighbors_IR
    hotspot = get_hotspot(grid)
    print(f"Iteration {i}, worst IR: {hotspot}")
    v_pads, g_pads = read_padfile(PAD_LOCATIONS)
    new_v_pads = []
    moved = 0
    for j in range(len(v_pads)):
        x_old, y_old = v_pads[j]
        neighbors = find_neighbors_IR(x_old, y_old, grid) #dictionary data
        forces = compute_forces(neighbors) #returns x and y forces in dictionary
        distances = distance_from_forces(forces, D)
        x_pos = x_old + distances["x"]
        y_pos = y_old + distances["y"]
        if(x_pos > GRID_MAX):
            x_pos = GRID_MAX
        if(y_pos > GRID_MAX):
            y_pos = GRID_MAX
        if(x_pos < 0):
            x_pos = 0
        if(y_pos < 0):
            y_pos = 0

        candidate = (x_pos, y_pos)
        remaining_old = v_pads[j+1:]
        site = snap_to_legal_site(candidate, legal_sites, g_pads, new_v_pads, remaining_old)
        if site == None:
            new_v_pads.append((x_old, y_old))
        else:
            new_v_pads.append(site)
            if(site != (x_old, y_old)):
                moved += 1
            
    print(f"Moved pads: {moved}")
    write_padfile(PAD_LOCATIONS, new_v_pads, g_pads)
    print(f"D: {D}")
    D = D*freeze_rate
    if moved == 0:
        break
    # if D < 1:
    #     break
