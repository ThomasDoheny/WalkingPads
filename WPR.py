# WP-R: Walking Pads - Refined variant

import subprocess
import math
import numpy as np

def read_padfile(file):
    vdd = []
    gnd = []
    with open(file) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
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
    return max(grid.items(), key=lambda x: x[1])

def run_voltspot():
    subprocess.run([
        "./voltspot",
        "-f", "example.flp",
        "-p", "example.ptrace",
        "-c", "pdn.config",
        "-gridvol_file", "steady.gridIR"
    ], cwd="voltspot")

def find_neighbors_IR(x, y, IR):
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
    return {"left": left, "right": right, "top": top, "bottom": bottom}

def compute_forces(data):
    force_x = data["right"] - data["left"]
    force_y = data["top"] - data["bottom"]
    return {"x": force_x, "y": force_y}

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

def get_max_ir():
    grid = read_grid_ir("voltspot/steady.gridIR")
    return get_hotspot(grid)[1], grid


sim_length = 1000
legal_sites = read_legal_padfile("voltspot/example.vgrid.padloc")

for i in range(sim_length):
    run_voltspot()
    grid = read_grid_ir("voltspot/steady.gridIR")
    hotspot = get_hotspot(grid)
    max_ir = hotspot[1]
    hotspot_loc = hotspot[0]
    print(f"Iteration {i}, worst IR: {hotspot}")

    v_pads, g_pads = read_padfile("voltspot/pads.vgrid.padloc")

    # WP-R: sort pads by distance to hotspot, nearest first
    v_pads_sorted = sorted(v_pads, key=lambda p: math.hypot(p[0]-hotspot_loc[0], p[1]-hotspot_loc[1]))

    improved = False
    new_v_pads = list(v_pads)  # copy to track accepted moves

    for pad in v_pads_sorted:
        idx = new_v_pads.index(pad)
        x_old, y_old = pad

        neighbors = find_neighbors_IR(x_old, y_old, grid)
        forces = compute_forces(neighbors)
        distances = distance_from_forces(forces)

        x_pos = min(72, max(0, x_old + distances["x"]))
        y_pos = min(72, max(0, y_old + distances["y"]))
        candidate = (x_pos, y_pos)

        occupied_without_current = [p for k, p in enumerate(new_v_pads) if k != idx]
        site = snap_to_legal_site(candidate, legal_sites, g_pads, occupied_without_current, [])

        if site is None or site == (x_old, y_old):
            continue

        # tentatively accept move and re-evaluate
        new_v_pads[idx] = site
        write_padfile("voltspot/pads.vgrid.padloc", new_v_pads, g_pads)
        run_voltspot()
        new_max_ir, grid = get_max_ir()

        if new_max_ir < max_ir:
            # accept: update hotspot and re-sort next iteration
            max_ir = new_max_ir
            hotspot_loc = get_hotspot(grid)[0]
            improved = True
            print(f"  Accepted move {(x_old, y_old)} -> {site}, new IR: {max_ir:.6f}")
        else:
            # reject: revert
            new_v_pads[idx] = (x_old, y_old)
            write_padfile("voltspot/pads.vgrid.padloc", new_v_pads, g_pads)

    print(f"Improved: {improved}")
    if not improved:
        print("Converged (no improving move found)")
        break