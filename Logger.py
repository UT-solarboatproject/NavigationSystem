import argparse
import csv
import pathlib
from datetime import datetime, timedelta, timezone

import matplotlib.pyplot as plt
import yaml

from Waypoint import Waypoint


class Logger:
    def __init__(self):
        jst = timezone(timedelta(hours=+9), "JST")
        present = datetime.now(jst)
        now = present.strftime("%Y-%m-%d-%H-%M-%S")
        self.filename = f"gpslog_{now}.csv"
        self.log_dir = pathlib.Path("log") / now
        self.log_dir.mkdir(exist_ok=True)

    def open_gps_log(self):
        self.f = open(self.log_dir / self.filename, "a")
        self.writer = csv.writer(self.f, lineterminator="\n")
        log_list = [
            "TIME_STAMP",
            "MODE",
            "LATITUDE",
            "LONGITUDE",
            "HEADING",
            "SPEED",
            "T_INDEX",
            "T_LATITUDE",
            "T_LONGITUDE",
            "T_BEARING",
            "T_DISTANCE",
            "SERVO_PW",
            "THR_PW",
            "ERR_BACK",
            "CURRENT",
            "VOLTAGE",
            "POWER",
        ]
        self.writer.writerow(log_list)

    def write_gps_log(self, log_list):
        self.writer.writerow(log_list)

    def close_gps_log(self):
        self.f.write("END\n")
        self.f.close()

    def save_waypoints_fig(self, waypoint, path):
        fig, ax = plt.subplots()
        for name, lat, lon in zip(waypoint.name, waypoint.latitude, waypoint.longitude):
            ax.scatter(lat, lon, label=name)
        ax.axis("equal")
        ax.legend()
        fig.savefig(self.log_dir / path.with_suffix(".png"))

    def save_params(self, params, path):
        with open(self.log_dir / path, "w") as f:
            yaml.dump(params, f)


def _load_waypoints(filename):
    path = pathlib.Path(filename)
    with open(path, "r") as f:
        params = yaml.safe_load(f)
    waypoint = Waypoint()
    for wp in params["waypoints"]:
        name = wp["name"]
        lat = wp["lat"]
        lon = wp["lon"]
        waypoint.add_point(lat, lon, name)
    return waypoint, path


def _parse_args():
    """
    input_file_path: input fileのpath
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file_path")
    parser.add_argument("-ww", "--write_waypoints_fig", action="store_true")
    parser.add_argument("-wl", "--write_log", action="store_true")
    args = parser.parse_args()
    return args


# test code
if __name__ == "__main__":
    args = _parse_args()
    logger = Logger()
    if args.write_log:
        logger.open_gps_log()
        logger.write_gps_log([1, 1, 1])
        logger.close_gps_log()
    if args.write_waypoints_fig:
        waypoint, path = _load_waypoints(args.input_file_path)
        logger.save_waypoints_fig(waypoint, path)
    with open(args.input_file_path, "r") as f:
        params = yaml.safe_load(f)
    logger.save_params(params, args.input_file_path)
