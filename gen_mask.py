from PIL import Image, ImageDraw
import yaml
import os
import numpy as np


MAP_YAML = "maps/map_eerc722.yaml"
MAP_PGM = "maps/map_eerc722.pgm"

KEEPOUT_MASK = "config/keepout_mask.pgm"
SPEED_MASK = "config/speed_mask.pgm"

# ── helpers ──────────────────────────────────────────────────────────────────
def load_map_info(yaml_path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    return data["resolution"], data["origin"]

def world_to_pixel(x, y, origin, resolution, height):
    """Convert world (x, y) metres → image (col, row) pixels."""
    origin_x, origin_y = origin[0], origin[1]
    col = int((x - origin_x) / resolution)
    row = int(height - (y - origin_y) / resolution)
    return (col, row)

# ── keepout mask ─────────────────────────────────────────────────────────────
def create_keepout_mask():
    """
    Keepout mask uses mode: trinary.
    Background = 255 (free, no keepout).
    Polygon    =   0 (occupied, keepout zone).
    """
    img = Image.open(MAP_PGM).convert("L")
    width, height = img.size

    # FIX: background must be 255 (free) so only the polygon is kept-out
    mask = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(mask)

    resolution, origin = load_map_info(MAP_YAML)

    # World coordinates — listed in correct polygon winding order (counter-clockwise)
    keepout_world = [
        (3.762526750564575,  0.9740602970123291),   # top-left
        (4.667067337036133,  0.9685339331626892),   # top-right
        (4.6624738693237305, -0.9884122014045715),  # bottom-right
        (3.6579577922821045, -1.002922534942627),   # bottom-left
    ]

    keepout_pixels = [
        world_to_pixel(x, y, origin, resolution, height)
        for x, y in keepout_world
    ]
    draw.polygon(keepout_pixels, fill=0)

    mask.save(KEEPOUT_MASK)
    print(f"Saved {KEEPOUT_MASK}")
    print(f"  Image size : {width} x {height} px")
    print(f"  Pixel coords: {keepout_pixels}")
    arr = np.array(mask)
    print(f"  Unique values in mask: {np.unique(arr)}")
    print(f"  Keepout pixels (value=0): {(arr == 0).sum()}")

# ── speed mask ───────────────────────────────────────────────────────────────
def create_speed_mask():
    """
    Speed mask uses mode: scale, occupied_thresh: 1.0, free_thresh: 0.0.

    Nav2 SpeedFilter formula:
        speed_limit = base + multiplier * raw_pixel_value
        (base=100, multiplier=-1.0)

    Pixel value → speed limit:
        255  →  100 + (-1.0 * 100) =   0%  [stop — avoid using as background!]
          0  →  100 + (-1.0 *   0) = 100%  [full speed]
         50  →  100 + (-1.0 *  50) =  50%  [half speed]
         75  →  100 + (-1.0 *  75) =  25%  [quarter speed]

    NOTE: mode:scale maps raw PGM byte (0-255) → OccupancyGrid int (0-100)
          via:  occ_value = (1 - pixel/255) * 100
          So the actual formula nav2 uses on the OccupancyGrid value is:
              speed_limit = 100 + (-1.0 * occ_value)

          PGM 255 (white) → occ 0   → speed limit 100% (no limit)  ← correct background
          PGM   0 (black) → occ 100 → speed limit   0% (stop)
          PGM 128 (gray)  → occ ~50 → speed limit  50%

    FIX: background must be 255 (white = full speed allowed).
         The speed zone polygon gets a darker value = more restriction.
    """
    img = Image.open(MAP_PGM).convert("L")
    width, height = img.size

    # FIX: background = 255 (white) = no speed restriction
    mask = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(mask)

    resolution, origin = load_map_info(MAP_YAML)

    # World coordinates in correct polygon winding order
    speed_world = [
        (2.0606272220611572, -1.0496567487716675),  # top-left
        (2.9753756523132324, -0.9926471710205078),  # top-right
        (2.957444667816162,  -3.0054500102996826),  # bottom-right
        (2.035498857498169,  -3.000837564468384),   # bottom-left
    ]

    speed_pixels = [
        world_to_pixel(x, y, origin, resolution, height)
        for x, y in speed_world
    ]

    # PGM 128 → OccupancyGrid ~50 → speed limit = 100 + (-1.0 * 50) = 50%
    draw.polygon(speed_pixels, fill=128)

    mask.save(SPEED_MASK)
    print(f"\nSaved {SPEED_MASK}")
    print(f"  Image size : {width} x {height} px")
    print(f"  Pixel coords: {speed_pixels}")
    arr = np.array(mask)
    print(f"  Unique values in mask: {np.unique(arr)}")
    print(f"  Speed-limited pixels (value=128): {(arr == 128).sum()}")

# ── main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(os.path.dirname(KEEPOUT_MASK), exist_ok=True)
    create_keepout_mask()
    create_speed_mask()
    print("\nDone. Copy both .pgm files to your config/ directory.")
    print("Also update speed_costmap_filter_info_server multiplier to -1.0")