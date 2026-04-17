# SA.py - Simulated Annealing pad placement

import subprocess
import math
import random

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
    sites = []
    with open(file) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            t, x, y = line.split()
            if t in ("V", "G"):
                sites.append((int(x), int(y)))
    return sites

def run_voltspot():
    result = subprocess.run([
        "./voltspot",
        "-f", "example.flp",
        "-p", "example.ptrace",
        "-c", "pdn.config",
        "-gridvol_file", "steady.gridIR"
    ], cwd="voltspot", capture_output=True, text=True)
    return result.stdout

def parse_voltspot_output(stdout):
    info = {}
    for line in stdout.splitlines():
        if "chip dimension" in line:
            info["chip_dim"] = line.split(":")[-1].strip()
        elif "supply voltage" in line:
            info["vdd"] = line.split(":")[-1].strip()
        elif "virtual grid size" in line:
            info["vgrid"] = line.split(":")[-1].strip()
        elif "pad grid size" in line:
            info["pgrid"] = line.split(":")[-1].strip()
        elif "number of pads" in line:
            info["npads"] = line.split(":")[-1].strip()
        elif "sum of current" in line:
            info["current"] = line.split(":")[-1].strip()
        elif "Max pad current" in line:
            info["max_pad_current"] = line.split(":")[-1].strip()
        elif "max on-chip IR drop" in line:
            info["max_ir"] = line.split(":")[-1].strip()
        elif "PDN static power loss" in line:
            info["power_loss"] = line.split(":")[-1].strip()
    return info

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

def find_nearby_legal_site(pad, legal_sites, occupied, max_dist):
    candidates = [
        s for s in legal_sites
        if s not in occupied and math.hypot(s[0]-pad[0], s[1]-pad[1]) <= max_dist
    ]
    if not candidates:
        return None
    return random.choice(candidates)

def print_info(iteration, hotspot, accepted, moves_per_temp, T, best_ir, info):
    print(f"Iteration {iteration}, worst IR: {hotspot}")
    print(f"Accepted moves: {accepted}/{moves_per_temp}")
    print(f"T: {T:.6f} | best IR so far: {best_ir:.6f}")
    print(f"1: chip dimension (width/height, meter):  {info.get('chip_dim', 'N/A')}")
    print(f"2: supply voltage vdd (Volt):             {info.get('vdd', 'N/A')}")
    print(f"3: virtual grid size (num_cols/num_rows): {info.get('vgrid', 'N/A')}")
    print(f"4: pad grid size (num_cols/num_rows):     {info.get('pgrid', 'N/A')}")
    print(f"5: number of pads (vdd/gnd):              {info.get('npads', 'N/A')}")
    print(f"6: sum of current (A):                    {info.get('current', 'N/A')}")
    print(f"7: Max pad current (A):                   {info.get('max_pad_current', 'N/A')}")
    print(f"8: max on-chip IR drop (%Vdd):            {info.get('max_ir', 'N/A')}")
    print(f"9: PDN static power loss (W):             {info.get('power_loss', 'N/A')}")

# ── Parameters ──────────────────────────────────────────────
T_start        = 0.005
T_end          = 1e-6
cooling_rate   = 0.95
moves_per_temp = 10
max_dist       = 20
# ────────────────────────────────────────────────────────────

legal_sites = read_legal_padfile("voltspot/example.vgrid.padloc")
vdd, gnd = read_padfile("voltspot/pads.vgrid.padloc")
gnd_set = set(gnd)

stdout = run_voltspot()
info = parse_voltspot_output(stdout)
grid = read_grid_ir("voltspot/steady.gridIR")
current_ir = get_hotspot(grid)[1]
current_hotspot = get_hotspot(grid)
best_ir = current_ir
best_vdd = vdd[:]

print(f"Starting SA | worst IR: {current_hotspot}")
print_info(0, current_hotspot, 0, moves_per_temp, T_start, best_ir, info)

T = T_start
iteration = 0

while T > T_end:
    accepted = 0
    for _ in range(moves_per_temp):
        occupied = set(vdd) | gnd_set
        idx = random.randint(0, len(vdd) - 1)
        old_pad = vdd[idx]
        new_pad = find_nearby_legal_site(old_pad, legal_sites, occupied - {old_pad}, max_dist)
        if new_pad is None:
            continue
        vdd[idx] = new_pad
        write_padfile("voltspot/pads.vgrid.padloc", vdd, gnd)
        stdout = run_voltspot()
        grid = read_grid_ir("voltspot/steady.gridIR")
        new_hotspot = get_hotspot(grid)
        new_ir = new_hotspot[1]
        delta = new_ir - current_ir
        if delta < 0 or random.random() < math.exp(-delta / T):
            current_ir = new_ir
            current_hotspot = new_hotspot
            accepted += 1
            if current_ir < best_ir:
                best_ir = current_ir
                best_vdd = vdd[:]
        else:
            vdd[idx] = old_pad

    iteration += 1
    info = parse_voltspot_output(stdout)
    print_info(iteration, current_hotspot, accepted, moves_per_temp, T, best_ir, info)
    T *= cooling_rate

write_padfile("voltspot/pads.vgrid.padloc", best_vdd, gnd)
print(f"\nDone. Best IR drop: {best_ir:.6f}")
