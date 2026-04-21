import random
import argparse

def read_full_padfile(file):
    pads = []
    with open(file) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            t, x, y = line.split()
            pads.append((t, int(x), int(y)))
    return pads   

def read_all_sites(file):
    sites = []
    with open(file) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            _, x, y = line.split()
            sites.append((int(x), int(y)))
    return sites

def write_padfile(file, vdd, gnd):
    with open(file, "w") as f:
        for x, y in vdd:
            f.write(f"V\t{x}\t{y}\n")
        for x, y in gnd:
            f.write(f"G\t{x}\t{y}\n")




# def build_clean_subset(full_file, out_file):
#     pads = read_full_padfile(full_file)

#     vdd = []
#     gnd = []

#     for t, x, y in pads:
#         gx = (x - 4) // 8
#         gy = (y - 4) // 8

#         # Keep G pads in a sparse uniform checkerboard-like pattern
#         if t == "G":
#             if (gx % 3 == 0) and (gy % 3 == 0):
#                 gnd.append((x, y))

#         # Keep V pads in a different interleaved pattern
#         elif t == "V":
#             if (gx % 3 == 1) and (gy % 3 == 1):
#                 vdd.append((x, y))

#     write_padfile(out_file, vdd, gnd)
#     print(f"Wrote {len(vdd)} V pads and {len(gnd)} G pads to {out_file}")


# if __name__ == "__main__":
#     build_clean_subset("example.vgrid.padloc", "new_pads.vgrid.padloc")


# def build_half_subset(full_file, out_file):
#     pads = read_full_padfile(full_file)

#     vdd = []
#     gnd = []

#     for t, x, y in pads:
#         gx = (x - 4) // 8
#         gy = (y - 4) // 8

#         # keep about half the sites
#         if (gx + gy) % 2 == 0:
#             if t == "V":
#                 vdd.append((x, y))
#             elif t == "G":
#                 gnd.append((x, y))

#     write_padfile(out_file, vdd, gnd)
#     print(f"Wrote {len(vdd)} V pads and {len(gnd)} G pads to {out_file}")

# if __name__ == "__main__":
#     build_half_subset("example.vgrid.padloc", "new_pads.vgrid.padloc")


def build_random_subset(full_file, out_file, keep_ratio=0.5, v_ratio=0.5, seed=42):
    random.seed(seed)

    sites = read_all_sites(full_file)
    random.shuffle(sites)

    keep_count = int(len(sites) * keep_ratio)
    kept_sites = sites[:keep_count]

    vdd = []
    gnd = []

    for site in kept_sites:
        if random.random() < v_ratio:
            vdd.append(site)
        else:
            gnd.append(site)

    write_padfile(out_file, vdd, gnd)

    print(f"Total sites: {len(sites)}")
    print(f"Kept: {len(kept_sites)}")
    print(f"V pads: {len(vdd)}")
    print(f"G pads: {len(gnd)}")

if __name__ == "__main__":
    # to be able to set legal_pad location and where the output is generated
    parser = argparse.ArgumentParser()
    parser.add_argument("--legal_pad_location", default = "voltspot/example.vgrid.padloc")
    parser.add_argument("--output_pad_location", default = "voltspot/new_pads.vgrid.padloc")
    args = parser.parse_args()
    build_random_subset(
        args.legal_pad_location,
        args.output_pad_location,
        keep_ratio=0.5,
        v_ratio=0.5,
        seed=42
    )