import argparse
import json
import re
import xml.etree.ElementTree as ET

import utm


def get_namespace(tree):
    match = re.match("^{(.*)}", tree.getroot().tag)
    if match:
        return match.groups()[0]
    else:
        return ""


def gpx2json(gpx_file, location, elevation_mul=1):
    tree = ET.parse(gpx_file)
    root = tree.getroot()

    namespace = {"": get_namespace(tree)}

    points = []

    lat, lon = map(float, location.split("/"))

    origo = {"lat": lat, "lon": lon}

    utm_origo = utm.from_latlon(origo["lat"], origo["lon"])

    for trkpt in root.findall(".//trkpt", namespace):
        ele = float(trkpt.find("ele", namespace).text)
        time = trkpt.find("time", namespace).text
        lat = float(trkpt.attrib["lat"])
        lon = float(trkpt.attrib["lon"])

        utm_coordinate = utm.from_latlon(lat, lon)

        x = utm_coordinate[0] - utm_origo[0]
        z = utm_coordinate[1] - utm_origo[1]

        if utm_origo[3] > "M":
            # North hemisphere
            z = -z

        point = {
            "time": time,
            "lat": lat,
            "lon": lon,
            "ele": ele * elevation_mul,
            "utm": utm_coordinate,
            "x": x,
            "z": z,
        }

        points.append(point)

    return points


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("location")
    parser.add_argument("--elevation-mul", type=int, default=1)
    args = parser.parse_args()

    with open(args.file) as f:
        print(json.dumps(gpx2json(f, args.location, args.elevation_mul)))
