from PIL import Image, ImageDraw
import yaml
import os
import numpy as np


MAP_YAML = "maps/map_eerc722.yaml"
MAP_PGM = "maps/map_eerc722.pgm"

KEEPOUT_MASK = "config/keepout_mask.pgm"
SPEED_MASK = "config/speed_mask.pgm"


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

def create_keepout_mask():
    """
    Keepout mask uses mode: trinary.
    Background = 255 (free, no keepout).
    Polygon    =   0 (occupied, keepout zone).
    """
    img = Image.open(MAP_PGM).convert("L")
    width, height = img.size

    mask = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(mask)

    resolution, origin = load_map_info(MAP_YAML)

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

def create_speed_mask():
    img = Image.open(MAP_PGM).convert("L")
    width, height = img.size

    mask = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(mask)

    resolution, origin = load_map_info(MAP_YAML)

    speed_world = [
        (2.9946084022521973, 0.9779025912284851),
        (3.016167163848877, -1.020748496055603),
        (1.9959399700164795, -0.9840879440307617),
        (1.995314598083496, 0.9934210777282715),
    ]

    speed_pixels = [
        world_to_pixel(x, y, origin, resolution, height)
        for x, y in speed_world
    ]

    # PGM ≈ 25 -> OccupancyGrid ≈ 90 -> speed limit ≈ 10%
    draw.polygon(speed_pixels, fill=25)

    mask.save(SPEED_MASK)
    print(f"\nSaved {SPEED_MASK}")
    print(f"  Image size : {width} x {height} px")
    print(f"  Pixel coords: {speed_pixels}")
    arr = np.array(mask)
    print(f"  Unique values in mask: {np.unique(arr)}")
    print(f"  Speed-limited pixels (value=25): {(arr == 25).sum()}")


if __name__ == "__main__":
    os.makedirs(os.path.dirname(KEEPOUT_MASK), exist_ok=True)
    create_keepout_mask()
    create_speed_mask()
    print("\nDone. Copy both .pgm files to your config/ directory.")
    print("Also update speed_costmap_filter_info_server multiplier to -1.0")
