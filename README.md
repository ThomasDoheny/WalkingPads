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

### 1. Generate a random pad placement

```bash
python3 generator.py
cp voltspot/new_pads.vgrid.padloc voltspot/pads.vgrid.padloc
```

### 2. Visualize the random baseline

```bash
cd voltspot
./voltspot -f example.flp -p example.ptrace -c pdn.config -gridvol_file baseline.gridIR
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

### 0. Edit the WP.py file
```python
FLP    = "../new_floorplan/alpha_ev6/ev6.flp"
PTRACE = "../new_floorplan/alpha_ev6/ev6_fixed.ptrace"
```

### 1. Generate a random pad placement (same as above)

```bash
python3 generator.py
cp voltspot/new_pads.vgrid.padloc voltspot/pads.vgrid.padloc
```

### 2. Visualize the random baseline

```bash
cd voltspot
./voltspot -f ../new_floorplan/alpha_ev6/ev6.flp -p ../new_floorplan/alpha_ev6/ev6_fixed.ptrace -c ../new_floorplan/alpha_ev6/ev6.config -gridvol_file baseline.gridIR
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