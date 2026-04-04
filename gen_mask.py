from PIL import Image, ImageDraw
import yaml
import os

MAP_YAML = "maps/map_eerc722.yaml"
MAP_PGM = "maps/map_eerc722.pgm"

KEEP_OUT_MASK = "config/keepout_mask.pgm"
SPEED_MASK = "config/speed_mask.pgm"



#i am not sure how this code is gonna seo we might wanna replace some sparts

def load_map_info(yaml_path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    return data["resolution"], data["origin"]

def world_to_pixel(x, y, origin, resolution, height):
    origin_x, origin_y, _ = origin
    col = int((x - origin_x) / resolution)
    row = int(height - ((y - origin_y) / resolution))
    return (col, row)

def create_keepout_mask():
    img = Image.open(MAP_PGM).convert("L")
    width, height = img.size

    mask = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(mask)

    resolution, origin = load_map_info(MAP_YAML)

    # we should replace this will the actual coordinates, i was just doin a test to see if the code works 
    keepout_world = [
        (-2.0, -1.0),
        (-1.0, -1.0),
        (-1.0,  0.5),
        (-2.0,  0.5),
    ]

    keepout_pixels = [world_to_pixel(x, y, origin, resolution, height) for x, y in keepout_world]
    draw.polygon(keepout_pixels, fill=0)

    mask.save(KEEP_OUT_MASK)

def create_speed_mask():
    img = Image.open(MAP_PGM).convert("L")
    width, height = img.size

    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)

    resolution, origin = load_map_info(MAP_YAML)

    #same here, we should replace this will the actual coordinates, i was just doin a test to see if the code works 

    speed_world = [
        (0.5, -2.0),
        (1.8, -2.0),
        (1.8, -1.2),
        (0.5, -1.2),
    ]

    speed_pixels = [world_to_pixel(x, y, origin, resolution, height) for x, y in speed_world]
    draw.polygon(speed_pixels, fill=1)

    mask.save(SPEED_MASK)

if __name__ == "__main__":
    os.makedirs("config", exist_ok=True)
    create_keepout_mask()
    create_speed_mask()
    print("Created keepout_mask.pgm and speed_mask.pgm")