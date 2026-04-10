- I ran this on Linux so hopefully this works for you, if not, ask chatGPT to help
- install superLU  with ""sudo apt install libsuperlu-dev"
- Install BLAS with "subo apt install libblas-dev liblapack-dev"
- Open the MakeFile and change the SUPERLULIB, SLU_HEADER, and BLASLIB fields to point to your installed libraries
- make clean, the make in terminal
- "./voltspot -f example.flp -p example.ptrace -c pdn.config -gridvol_file steady.gridIR" to run voltspot
- I wrote three python scripts, "WP.py" "WPN.py" and "generator.py"
- generator.py created my list of pads in new_pads.vgrid.padloc. Then I would just copy and overwrite what was in pads.vgrid.padloc. "python3 generator.py"
-WPN.py doesn't work yet so just ignore
-WP.py run walking pads freezing, "python3 WP.py" to run simulation
- "perl plot_onchipIR.pl steady.gridIR" generates a power map image into the folder, need to have perl installed "sudo apt install perl"


