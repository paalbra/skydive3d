import argparse
import json
import xml.etree.ElementTree as ET

import utm


def gpx2json(gpx_file, location):
    tree = ET.parse(gpx_file)
    root = tree.getroot()

    points = []

    lat, lon = map(float, location.split("/"))

    origo = {"lat": lat, "lon": lon}

    utm_origo = utm.from_latlon(origo["lat"], origo["lon"])

    for trkpt in root.findall(".//trkpt"):
        ele = float(trkpt.find("ele").text)
        time = trkpt.find("time").text
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
            "ele": ele,
            "utm": utm_coordinate,
            "x": x,
            "z": z,
        }

        points.append(point)

    print(json.dumps(points))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("location")
    args = parser.parse_args()

    with open(args.file) as f:
        gpx2json(f, args.location)
