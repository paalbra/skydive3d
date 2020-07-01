import json
import sys
import xml.etree.ElementTree as ET

import utm

if __name__ == "__main__":
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    points = []

    lat, lon = sys.argv[2].split("/")
    lat, lon = float(lat), float(lon)

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
