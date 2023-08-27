import argparse
import time
import urllib.request
import pathlib

import mercantile
import PIL.Image
import utm


def download_tile(xtile, ytile, zoom_level):
    time.sleep(0.2)
    url = f"https://a.tile.openstreetmap.org/{zoom_level}/{xtile}/{ytile}.png"
    request = urllib.request.Request(url, headers={"User-Agent": "https://github.com/paalbra/skydive3d"})
    response = urllib.request.urlopen(request)
    content = response.read()
    return content


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("location")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--render-size", type=float, default=0.02)
    parser.add_argument("--zoom-level", type=int, default=14)
    parser.add_argument("--cache", default="cache")
    parser.add_argument("--output", default="html")
    args = parser.parse_args()

    cache_directory = pathlib.Path(args.cache)
    output_directory = pathlib.Path(args.output)

    if not cache_directory.exists():
        cache_directory.mkdir()
    if not output_directory.exists():
        output_directory.mkdir()

    if cache_directory.exists() and not cache_directory.is_dir():
        raise Exception(f"Cache path ('{cache_directory}') is not a directory!")
    if output_directory.exists() and not output_directory.is_dir():
        raise Exception(f"Output path ('{output_directory}') is not a directory!")

    lat, lon = map(float, args.location.split("/"))

    lat_nw, lon_nw = (lat + args.render_size, lon - args.render_size*2)
    lat_se, lon_se = (lat - args.render_size, lon + args.render_size*2)

    # Align to tiles
    tile_nw_x, tile_nw_y, _ = mercantile.tile(lon_nw, lat_nw, args.zoom_level)
    lon_nw, lat_nw = mercantile.ul(tile_nw_x, tile_nw_y, args.zoom_level)

    tile_se_x, tile_se_y, _ = mercantile.tile(lon_se, lat_se, args.zoom_level)
    lon_se, lat_se = mercantile.ul(tile_se_x, tile_se_y, args.zoom_level)

    utm_nw = utm.from_latlon(lat_nw, lon_nw)
    utm_se = utm.from_latlon(lat_se, lon_se)

    print(f"NW UTM: {utm_nw}")
    print(f"SE UTM: {utm_se}")
    print(f"Width: {utm_se[0] - utm_nw[0]}, height: {utm_se[1] - utm_nw[1]}")

    print(f"NW tile: {tile_nw_x}/{tile_nw_y}")
    print(f"SE tile: {tile_se_x}/{tile_se_y}")
    print(f"NW location: {lat_nw}/{lon_nw}")
    print(f"SE location: {lat_se}/{lon_se}")

    if args.download:
        for y in range(tile_nw_y, tile_se_y):
            for x in range(tile_nw_x, tile_se_x):
                print(x, y)
                content = download_tile(x, y, args.zoom_level)
                with open(pathlib.Path(cache_directory / f"{args.zoom_level}-{x}-{y}.png"), "wb") as f:
                    f.write(content)

    merged_image = PIL.Image.new('RGB', ((tile_se_x - tile_nw_x)*256, (tile_se_y - tile_nw_y)*256))
    for x in range(tile_nw_x, tile_se_x):
        for y in range(tile_nw_y, tile_se_y):
            image = PIL.Image.open(pathlib.Path(cache_directory / f"{args.zoom_level}-{x}-{y}.png"))
            x_px = (x - tile_nw_x)*256
            y_px = (y - tile_nw_y)*256
            merged_image.paste(image, (x_px, y_px))

    merged_image.save(pathlib.Path(output_directory / "merged.png"))
