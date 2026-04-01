import rclpy
from rclpy.node import Node
import os
import yaml
import rclpy
import numpy as np
from PIL import Image
from math import pi, cos, sin


def get_map(yaml_path: str):
    with open(yaml_path, "r") as f:
        info = yaml.safe_load(f)

    image_path = info["image"]
    resolution = float(info["resolution"])
    origin = info["origin"]

    yaml_dir = os.path.dirname(os.path.abspath(yaml_path))
    abs_image_path = os.path.join(yaml_dir, image_path)

    img = Image.open(abs_image_path)
    grid = np.array(img)

    return grid, resolution, origin

class OccupancyGrid(Node):

    def __init__(self):
        super().__init__("og_node")

        self.z = None
        self.beam_angles = None 

        self.map_loc = "/home/progress/robotics/MCL/maps/map_jackal_sim.yaml"
        self.grid, self.resolution, self.origin = get_map(self.map_loc)
        self.h, self.w = self.grid.shape



    def world_to_map(x, y, origin, resolution, height):
        og_x, og_y, _ = origin

        mx = int((x - og_x) / resolution)
        my = int((y - og_y) / resolution)

        # Flip image coordinates because image row 0 is top
        my_img = height - 1 - my
        return mx, my_img
    
    def map_to_world(self, mx, my_img, height):

        og_x, og_y, _ = self.origin
        my = height - 1 - my_img
        x = og_x + (mx + 0.5) * self.resolution
        y = og_y + (my + 0.5) * self.resolution
        return x, y


def is_occupied(grid, mx, my, occ_threshold=250):
    h, w = grid.shape

    if mx < 0 or mx >= w or my < 0 or my >= h:
        return True

    pixel = grid[my, mx]
    return pixel < occ_threshold


def main():
    rclpy.init()

    node = OccupancyGrid()
    rclpy.spin(node)

    node.destroy_node() 

    rclpy.shutdown()


if __name__ == '__main__':
    main()
