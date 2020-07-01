import sys
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
    print(sys.argv)
    zoom_level = 14
    render_size = 0.02  # In degrees

    lat, lon = sys.argv[1].split("/")
    lat, lon = float(lat), float(lon)

    lat_nw, lon_nw = (lat + render_size, lon - render_size*2)
    lat_se, lon_se = (lat - render_size, lon + render_size*2)

    print(f"{lat_nw}/{lon_nw}")
    print(f"{lat_se}/{lon_se}")

    # Align to tiles
    temp_xtile, temp_ytile, _ = mercantile.tile(lon_nw, lat_nw, zoom_level)
    lon_nw, lat_nw = mercantile.ul(temp_xtile, temp_ytile, zoom_level)
    xtile_nw, ytile_nw, _ = mercantile.tile(lon_nw, lat_nw, zoom_level)

    temp_xtile, temp_ytile, _ = mercantile.tile(lon_se, lat_se, zoom_level)
    lon_se, lat_se = mercantile.ul(temp_xtile, temp_ytile, zoom_level)
    xtile_se, ytile_se, _ = mercantile.tile(lon_se, lat_se, zoom_level)

    print("nw", xtile_nw, ytile_nw)
    print("se", xtile_se, ytile_se)

    if sys.argv[2] == "d":
        for y in range(ytile_nw, ytile_se):
            for x in range(xtile_nw, xtile_se):
                print(x, y)
                content = download_tile(x, y, zoom_level)
                with open(f"{zoom_level}-{x}-{y}.png", "wb") as f:
                    f.write(content)

    merged_image = PIL.Image.new('RGB', ((xtile_se - xtile_nw)*256, (ytile_se - ytile_nw)*256))
    for x in range(xtile_nw, xtile_se):
        for y in range(ytile_nw, ytile_se):
            image = PIL.Image.open(f"{zoom_level}-{x}-{y}.png")
            x_px = (x - xtile_nw)*256
            y_px = (y - ytile_nw)*256
            merged_image.paste(image, (x_px, y_px))

    merged_image.save("merged.png")

    utm_nw = utm.from_latlon(lat_nw, lon_nw)
    utm_se = utm.from_latlon(lat_se, lon_se)

    print(utm_nw)
    print(utm_se)
    print(utm_se[0] - utm_nw[0], utm_se[1] - utm_nw[1])

    random_pos = utm.from_latlon(59.2911, 10.3708)
    print("TEST", (random_pos[0] - utm_nw[0], random_pos[1] - utm_nw[1]))
