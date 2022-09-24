import argparse
import json
import logging
import re
import time
import urllib.request
import xml.etree.ElementTree as ET

import mercantile
import PIL.Image
import utm


TILE_SIZE = 256


def download_tile(x, y, zoom_level):
    url = f"https://a.tile.openstreetmap.org/{zoom_level}/{x}/{y}.png"
    request = urllib.request.Request(url, headers={"User-Agent": "https://github.com/paalbra/skydive3d"})
    response = urllib.request.urlopen(request)
    content = response.read()
    return content


def get_tile_coordinates(location, render_size, zoom_level):
    lat, lon = map(float, location.split("/"))

    # Create a box around location, based on render_size
    lat_nw, lon_nw = (lat + render_size, lon - render_size*2)
    lat_se, lon_se = (lat - render_size, lon + render_size*2)

    # Align to tiles
    tile_nw_x, tile_nw_y, _ = mercantile.tile(lon_nw, lat_nw, zoom_level)
    lon_nw, lat_nw = mercantile.ul(tile_nw_x, tile_nw_y, zoom_level)
    tile_se_x, tile_se_y, _ = mercantile.tile(lon_se, lat_se, zoom_level)
    lon_se, lat_se = mercantile.ul(tile_se_x, tile_se_y, zoom_level)

    utm_nw = utm.from_latlon(lat_nw, lon_nw)
    utm_se = utm.from_latlon(lat_se, lon_se)

    width = utm_se[0] - utm_nw[0]
    height = utm_se[1] - utm_nw[1]

    return {
        "tile_nw": (tile_nw_x, tile_nw_y),
        "tile_se": (tile_se_x, tile_se_y),
        "width": width,
        "height": height,
    }


def get_namespace(tree):
    match = re.match("^{(.*)}", tree.getroot().tag)
    if match:
        return match.groups()[0]
    else:
        return ""


def download_tiles(tile_nw, tile_se, zoom_level):
    tile_nw_x, tile_nw_y = tile_nw
    tile_se_x, tile_se_y = tile_se

    for y in range(tile_nw_y, tile_se_y):
        for x in range(tile_nw_x, tile_se_x):
            #print(x, y)
            content = download_tile(x, y, zoom_level)
            with open(f"{zoom_level}-{x}-{y}.png", "wb") as f:
                f.write(content)
            time.sleep(0.2)


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


def merge_tiles(tile_nw, tile_se, zoom_level):
    tile_nw_x, tile_nw_y = tile_nw
    tile_se_x, tile_se_y = tile_se

    merged_image = PIL.Image.new("RGB", ((tile_se_x - tile_nw_x)*TILE_SIZE, (tile_se_y - tile_nw_y)*TILE_SIZE))
    for x in range(tile_nw_x, tile_se_x):
        for y in range(tile_nw_y, tile_se_y):
            image = PIL.Image.open(f"{zoom_level}-{x}-{y}.png")
            x_px = (x - tile_nw_x)*TILE_SIZE
            y_px = (y - tile_nw_y)*TILE_SIZE
            merged_image.paste(image, (x_px, y_px))

    merged_image.save("html/merged.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("location")
    parser.add_argument("file")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--render-size", type=float, default=0.02)
    parser.add_argument("--zoom-level", type=int, default=14)
    parser.add_argument("--elevation-mul", type=int, default=1)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    tile_coordinates = get_tile_coordinates(args.location, args.render_size, args.zoom_level)
    if args.download:
        download_tiles(tile_coordinates["tile_nw"], tile_coordinates["tile_se"], args.zoom_level)
    merge_tiles(tile_coordinates["tile_nw"], tile_coordinates["tile_se"], args.zoom_level)

    with open(args.file) as f:
        points = gpx2json(f, args.location, args.elevation_mul)

    with open("html/data.js", "w") as f:
        f.write(f"width = {tile_coordinates['width']};\nheight = {tile_coordinates['height']};\npoints = ")
        digest = [{"x": point["x"], "z": point["z"], "ele": point["ele"]} for point in points]
        f.write(json.dumps(digest))
        f.write(";\n")
