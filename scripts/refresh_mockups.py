#!/usr/bin/env python3
"""Refresh the version strings inside the README mockup PNGs.

The mockups in Images/mockups/ are generated illustrations (not photos); the
original full generators were ad-hoc and are gone, so this script only
*patches the version text* at fixed coordinates: it fills the old text with
the sampled background color and draws the new string on top. Re-running is
idempotent as long as the patch boxes below stay generous.

Patched spots:
  printer-screens.png       update tile ("Installed: vX / Latest: vY"),
                            About tile ("FW: vY"), WiFi-info tile ("FW vY")
  web-dashboard.png         "Firmware Y" under the title
  firmware-update-page.png  "Current version: Y" (centered line)

Versions: "latest" comes from FIRMWARE_VERSION in platformio.ini, "installed"
(the update tile's old version) from the newest git tag below it - override
with --installed. Run before committing a release:

  %USERPROFILE%\\.platformio\\penv\\Scripts\\python.exe scripts\\refresh_mockups.py

Needs Pillow in that python (pip install pillow, one-time).
"""

import argparse
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
MOCKUPS = REPO_ROOT / "Images" / "mockups"
CONSOLA = r"C:\Windows\Fonts\consola.ttf"
SEGOE = r"C:\Windows\Fonts\segoeui.ttf"

ORANGE = (232, 114, 12)
BLUE = (132, 188, 248)
PAGE_BLUE = (132, 188, 248)


def read_latest_version():
    ini = (REPO_ROOT / "platformio.ini").read_text(encoding="utf-8")
    versions = set(re.findall(r'FIRMWARE_VERSION=\\"(\d+\.\d+\.\d+)\\"', ini))
    if len(versions) != 1:
        raise SystemExit(f"expected one FIRMWARE_VERSION, found {versions or 'none'}")
    return versions.pop()


def semver_key(v):
    return tuple(int(p) for p in v.split("."))


def read_installed_version(latest):
    """Newest git tag strictly below `latest` (the mockup shows an update
    being available: Installed < Latest)."""
    out = subprocess.run(["git", "tag", "-l", "v*"], cwd=REPO_ROOT,
                         capture_output=True, text=True, check=True).stdout
    tags = [t.strip().lstrip("v") for t in out.splitlines()
            if re.fullmatch(r"v\d+\.\d+\.\d+", t.strip())]
    older = [t for t in tags if semver_key(t) < semver_key(latest)]
    return max(older, key=semver_key) if older else latest


def patch(img, draw, box, text_runs, probe):
    """Fill `box` with the bg color sampled at `probe`, then draw the
    (x_offset, text, font, color) runs starting at the box origin."""
    bg = img.getpixel(probe)
    draw.rectangle(box, fill=bg, outline=bg)
    for dx, text, font, color in text_runs:
        draw.text((box[0] + dx, box[1]), text, font=font, fill=color)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--installed", help="version shown as 'Installed:' on the "
                    "update tile (default: newest git tag below the current)")
    args = ap.parse_args()

    latest = read_latest_version()
    installed = args.installed or read_installed_version(latest)
    print(f"mockups -> Installed: v{installed}, Latest/FW: v{latest}")

    mono34 = ImageFont.truetype(CONSOLA, 34)
    mono28 = ImageFont.truetype(CONSOLA, 28)
    mono26 = ImageFont.truetype(CONSOLA, 26)
    seg21 = ImageFont.truetype(SEGOE, 21)
    seg24 = ImageFont.truetype(SEGOE, 24)

    # --- printer-screens.png (2080x1920, 4x3 LCD tile collage) ---
    p = MOCKUPS / "printer-screens.png"
    img = Image.open(p).convert("RGB")
    d = ImageDraw.Draw(img)
    # update tile, two mono lines
    patch(img, d, (1466, 1100, 1886, 1144),
          [(0, f"Installed: v{installed}", mono34, (224, 224, 224))], (1900, 1100))
    patch(img, d, (1466, 1148, 1886, 1192),
          [(0, f"Latest: v{latest}", mono34, BLUE)], (1900, 1148))
    # About tile: "FW:" orange + value white
    patch(img, d, (786, 1560, 1106, 1600),
          [(0, "FW:", mono28, ORANGE), (62, f"v{latest}", mono28, (238, 238, 238))],
          (1100, 1565))
    # WiFi-info tile, small gray line
    patch(img, d, (1464, 1705, 1724, 1741),
          [(0, f"FW v{latest}", mono26, (170, 170, 170))], (1800, 1705))
    img.save(p)
    print(f"  {p.name} ok")

    # --- web-dashboard.png (1120x1440) ---
    p = MOCKUPS / "web-dashboard.png"
    img = Image.open(p).convert("RGB")
    d = ImageDraw.Draw(img)
    patch(img, d, (110, 276, 330, 304),
          [(0, f"Firmware {latest}", seg21, (170, 170, 170))], (400, 285))
    img.save(p)
    print(f"  {p.name} ok")

    # --- firmware-update-page.png (1000x1000), centered blue line ---
    p = MOCKUPS / "firmware-update-page.png"
    img = Image.open(p).convert("RGB")
    d = ImageDraw.Draw(img)
    text = f"Current version: {latest}"
    bb = seg24.getbbox(text)
    bg = img.getpixel((700, 497))
    d.rectangle((300, 482, 700, 516), fill=bg, outline=bg)
    d.text((500 - (bb[2] - bb[0]) / 2, 484), text, font=seg24, fill=PAGE_BLUE)
    img.save(p)
    print(f"  {p.name} ok")


if __name__ == "__main__":
    main()
