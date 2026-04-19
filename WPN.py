# WP-N: Walking Pads - Neighbor variant

import subprocess
import math
# import numpy as np

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
        "-f", "example.flp",
        "-p", "example.ptrace",
        "-c", "pdn.config",
        "-gridvol_file", "steady.gridIR"
    ], cwd="voltspot")

def find_neighbors_IR(x, y, IR): #grid is 73 by 73
    center = IR[(x, y)]
    if (x == 0):
        left = center
    else:
        left = IR[(x-1, y)]
    if (x == 72):
        right = center
    else:
        right = IR[(x+1, y)]
    if (y == 0):
        bottom = center
    else:
        bottom = IR[(x, y-1)]
    if (y == 72):
        top = center
    else:
        top = IR[(x, y+1)]
    return { "left":left,"right":right, "top":top, "bottom":bottom } 

def compute_forces(data):
    force_x = data["right"] - data["left"]
    force_y = data["top"] - data["bottom"]
    return {"x":force_x, "y":force_y} # dictionary

def sign(x):
    return -1 if x<0 else 1




def distance_from_forces(data):
    # WP-N: move exactly 1 step in the dominant direction only
    x_force = data["x"]
    y_force = data["y"]
    magnitude = math.hypot(x_force, y_force)
    if(magnitude < 1e-12):
        return {"x": 0, "y": 0}
    
    if abs(x_force) > abs(y_force):
        if sign(x_force) == -1:
            x_move = -8 #8 is the pad pitch
            y_move = 0
        else:
            x_move = 8
            y_move = 0
    else:
        if sign(y_force) == -1:
            x_move = 0
            y_move = -8
        else:
            x_move = 0
            y_move = 8
    return {"x":x_move, "y":y_move}

    # if abs(x_force) > abs(y_force):
    #     if np.sign(x_force) == -1:
    #         x_move = -1
    #         y_move = 0
    #     else:
    #         x_move = 1
    #         y_move = 0
    # else:
    #     if np.sign(y_force) == -1:
    #         x_move = 0
    #         y_move = -1
    #     else:
    #         x_move = 0
    #         y_move = 1
    # return {"x":x_move, "y":y_move}
    

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

def check_oscillation(history, window=6):
    # WP-N treats oscillation as convergence per the paper
    if len(history) < window:
        return False
    recent = history[-window:]
    return recent[0] == recent[2] == recent[4] and recent[1] == recent[3] == recent[5]


sim_length = 1000
legal_sites = read_legal_padfile("voltspot/example.vgrid.padloc")
pad_history = []

for i in range(sim_length):
    run_voltspot()
    grid = read_grid_ir("voltspot/steady.gridIR") #use this as input to find_neighbors_IR
    hotspot = get_hotspot(grid)
    print(f"Iteration {i}, worst IR: {hotspot}")
    v_pads, g_pads = read_padfile("voltspot/pads.vgrid.padloc")
    new_v_pads = []
    moved = 0
    for j in range(len(v_pads)):
        x_old, y_old = v_pads[j]
        neighbors = find_neighbors_IR(x_old, y_old, grid) #dictionary data
        forces = compute_forces(neighbors) #returns x and y forces in dictionary
        distances = distance_from_forces(forces)
        x_pos = x_old + distances["x"]
        y_pos = y_old + distances["y"]
        if(x_pos > 72):
            x_pos = 72
        if(y_pos > 72):
            y_pos = 72
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
            if site != (x_old, y_old):
                moved += 1

    print(f"Moved pads: {moved}")
    write_padfile("voltspot/pads.vgrid.padloc", new_v_pads, g_pads)

    pad_history.append(tuple(new_v_pads))
    if moved == 0 or check_oscillation(pad_history):
        print("Converged (no movement or oscillation detected)")
        break