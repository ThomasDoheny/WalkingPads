# WalkingPads

## Setup

### Dependencies

```bash
sudo apt install libsuperlu-dev libblas-dev liblapack-dev perl imagemagick
pip install numpy --break-system-packages
```

### Build VoltSpot

```bash
cd voltspot
make clean && make
cd ..
```

> If the Makefile needs to be adjusted for your system, open `voltspot/Makefile` and update the `SUPERLULIB`, `SLU_HEADER`, and `BLASLIB` fields to point to your installed libraries.

## Usage

### 0. Modify WP.py file
```python
FLOORPLAN     = "example.flp"
PTRACE        = "example.ptrace"
CONFIGURATION = "pdn.config"
LEGAL_PADLOC  = "voltspot/example.vgrid.padloc"
PAD_LOCATIONS = "voltspot/pads.vgrid.padloc"
GRID_MAX      = 72
```

### 1. Generate a random pad placement

```bash
python3 generator.py
cp voltspot/new_pads.vgrid.padloc voltspot/pads.vgrid.padloc
```

### 2. Visualize the random baseline

```bash
cd voltspot
./voltspot -f example.flp -p example.ptrace -c pdn.config -padloc_file_in pads.vgrid.padloc -gridvol_file baseline.gridIR
perl plot_onchipIR.pl baseline.gridIR
mv baseline.gif ../baseline.gif
cd ..
display baseline.gif &
```

### 3. Run an algorithm

**Walking Pads (WP-F):**
```bash
python3 WP.py
```

**Walking Pads (WP-N):**
```bash
python3 WPN.py
```

**Walking Pads (WP-R):**
```bash
python3 WPR.py
```

**Simulated Annealing (SA):**
```bash
python3 SA.py
```

> Both algorithms use `seed=42` in `generator.py`, so re-running `generator.py` and copying the result before each algorithm gives a fair comparison from the same starting placement.

### 4. Visualize result

```bash
cd voltspot
perl plot_onchipIR.pl steady.gridIR
mv steady.gif ../result.gif
cd ..
display result.gif &
```

## Scripts

- `generator.py` — generates a random starting pad placement into `voltspot/new_pads.vgrid.padloc`
- `WP.py` — Walking Pads Freezing algorithm
- `WPN.py` — Walking Pads Neighbor variant
- `WPR.py` — Walking Pads Refined variant
- `SA.py` — Simulated Annealing optimizer


## Usage if using ev6 floorplan

### 0. Edit the WP.py file and regenerate the padloc file for the new 159x159 grid
```python
FLP    = "../new_floorplan/alpha_ev6/ev6.flp"
PTRACE = "../new_floorplan/alpha_ev6/ev6_fixed.ptrace"
LEGAL_PADLOC = "voltspot/ev6.vgrid.padloc"
PAD_LOCATIONS = "voltspot/pads.vgrid.padloc"
GRID_MAX = 158 #this value was obtained running voltspot and seeing the actual virtual grid size it used
```
```bash
cd voltspot
./voltspot -f ../new_floorplan/alpha_ev6/ev6.flp \
           -p ../new_floorplan/alpha_ev6/ev6_fixed.ptrace \
           -c ../new_floorplan/alpha_ev6/ev6.config \
           -run_PDN 1 \
           -PDN_padconfig 1 \
           -padloc_file_out ev6.vgrid.padloc
```

### 1. Generate a random pad placement (same as above)

```bash
cd ..
python3 generator.py --legal_pad_location voltspot/ev6.vgrid.padloc --output_pad_location voltspot/pads.vgrid.padloc
```

### 2. Visualize the random baseline

```bash
cd voltspot
./voltspot -f ../new_floorplan/alpha_ev6/ev6.flp -p ../new_floorplan/alpha_ev6/ev6_fixed.ptrace -c ../new_floorplan/alpha_ev6/ev6.config -PDN_padconfig 0 -padloc_file_in pads.vgrid.padloc -gridvol_file baseline.gridIR
perl plot_onchipIR.pl baseline.gridIR
mv baseline.gif ../baseline.gif
cd ..
display baseline.gif &
```

### 3. Run an algorithm (same as above)

**Walking Pads (WP-F):**
```bash
python3 WP.py
```

### 4. Visualize result (same as above)

```bash
cd voltspot
perl plot_onchipIR.pl steady.gridIR
mv steady.gif ../result.gif
cd ..
display result.gif &
```

### NOTE

To run WP.py faster, you might consider having a keep_ratio = 0.3 in generator.py (fewer possiblities for pad placement so faster), D=10 in WP.py (so we start with smaller steps), freeze_rate = 0.95 such that it converges faster.
