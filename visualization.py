import argparse

import matplotlib.pyplot as plt
import yaml


def parse_args():
    """
    input_file_path: input fileのpath
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file_path")
    args = parser.parse_args()
    return args


def visualize_waypoints(filename):
    with open(filename, "r") as f:
        params = yaml.safe_load(f)

    for wp in params["waypoints"]:
        name = wp["name"]
        lat = wp["lat"]
        lon = wp["lon"]
        plt.scatter(lat, lon, label=name)
    plt.axis("equal")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    args = parse_args()
    visualize_waypoints(args.input_file_path)
