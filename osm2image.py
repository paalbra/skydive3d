import argparse
import time
import urllib.request

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
    args = parser.parse_args()

    lat, lon = map(float, args.location.split("/"))

    lat_nw, lon_nw = (lat + args.render_size, lon - args.render_size*2)
    lat_se, lon_se = (lat - args.render_size, lon + args.render_size*2)

    print(f"{lat_nw}/{lon_nw}")
    print(f"{lat_se}/{lon_se}")

    # Align to tiles
    tile_nw_x, tile_nw_y, _ = mercantile.tile(lon_nw, lat_nw, args.zoom_level)
    lon_nw, lat_nw = mercantile.ul(tile_nw_x, tile_nw_y, args.zoom_level)

    tile_se_x, tile_se_y, _ = mercantile.tile(lon_se, lat_se, args.zoom_level)
    lon_se, lat_se = mercantile.ul(tile_se_x, tile_se_y, args.zoom_level)

    print("nw", tile_nw_x, tile_nw_y)
    print("se", tile_se_x, tile_se_y)

    if args.download:
        for y in range(tile_nw_y, tile_se_y):
            for x in range(tile_nw_x, tile_se_x):
                print(x, y)
                content = download_tile(x, y, args.zoom_level)
                with open(f"{args.zoom_level}-{x}-{y}.png", "wb") as f:
                    f.write(content)

    merged_image = PIL.Image.new('RGB', ((tile_se_x - tile_nw_x)*256, (tile_se_y - tile_nw_y)*256))
    for x in range(tile_nw_x, tile_se_x):
        for y in range(tile_nw_y, tile_se_y):
            image = PIL.Image.open(f"{args.zoom_level}-{x}-{y}.png")
            x_px = (x - tile_nw_x)*256
            y_px = (y - tile_nw_y)*256
            merged_image.paste(image, (x_px, y_px))

    merged_image.save("merged.png")

    utm_nw = utm.from_latlon(lat_nw, lon_nw)
    utm_se = utm.from_latlon(lat_se, lon_se)

    print(utm_nw)
    print(utm_se)
    print(utm_se[0] - utm_nw[0], utm_se[1] - utm_nw[1])

    random_pos = utm.from_latlon(59.2911, 10.3708)
    print("TEST", (random_pos[0] - utm_nw[0], random_pos[1] - utm_nw[1]))
