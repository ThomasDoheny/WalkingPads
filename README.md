# WalkingPads

## Setup

### Dependencies

```bash
sudo apt install libsuperlu-dev libblas-dev liblapack-dev perl imagemagick
```

### Build VoltSpot

```bash
cd voltspot
make clean && make
cd ..
```

> If the Makefile needs to be adjusted for your system, open `voltspot/Makefile` and update the `SUPERLULIB`, `SLU_HEADER`, and `BLASLIB` fields to point to your installed libraries.

## Usage

### Run VoltSpot directly

```bash
cd voltspot
./voltspot -f example.flp -p example.ptrace -c pdn.config -gridvol_file steady.gridIR
cd ..
```

### Generate a random pad placement

```bash
python3 generator.py
cp voltspot/new_pads.vgrid.padloc voltspot/pads.vgrid.padloc
```

### Run Walking Pads (WP-F)

```bash
python3 WP.py
```

### Visualize results

```bash
perl voltspot/plot_onchipIR.pl voltspot/steady.gridIR
display voltspot/steady.gif &
```

## Scripts

- `generator.py` — generates a random starting pad placement into `voltspot/new_pads.vgrid.padloc`
- `WP.py` — Walking Pads freezing algorithm
- `WPN.py` — WIP
