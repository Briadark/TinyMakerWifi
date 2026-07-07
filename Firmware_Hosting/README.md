# Firmware hosting for self-update (GitHub Pages)

The printer's **System → Update** screen can check for a newer firmware and
install it over WiFi with no computer ("Install"). For that to work, two files
must be reachable over HTTPS from a stable URL. We host them on **GitHub Pages**
(the `gh-pages` branch), which serves a single host with no redirects — the
ESP32's TLS + `httpUpdate` handles that cleanly.

The URL the firmware checks is set in `src/Network.ino`:

```c
#define OTA_VERSION_URL "https://slibbinas.github.io/TinyMakerWifi/version.txt"
```

## Files to publish on `gh-pages`

1. **`version.txt`** — two lines: latest version, then the direct firmware URL.
   Use `Firmware_Hosting/version.txt` in this repo as the template:

   ```
   0.7.0
   https://slibbinas.github.io/TinyMakerWifi/firmware.bin
   ```

2. **`firmware.bin`** — the app-only image (OTA image, **not** `firmware-full.bin`).
   Built at `C:/PIO-build/TinyMakerWiFi/tinymaker/firmware.bin`.

## One-time setup

1. Create the `gh-pages` branch (can be an orphan branch with only these files).
2. In the repo: **Settings → Pages → Build and deployment → Source: Deploy from a
   branch → `gh-pages` / root**.
3. Confirm the files are live:
   - `https://slibbinas.github.io/TinyMakerWifi/version.txt`
   - `https://slibbinas.github.io/TinyMakerWifi/firmware.bin`

## Each release

1. Bump `FIRMWARE_VERSION` in `platformio.ini` (e.g. `0.7.0` → `0.8.0`) and build.
2. Copy the new `firmware.bin` to the `gh-pages` branch.
3. Update `version.txt` on `gh-pages` with the new version number (the URL stays
   the same). Commit/push.

The version check compares `MAJOR.MINOR.PATCH`, so "Install" only lights up when
`version.txt` is strictly newer than the running firmware.

> This is designed to grow into a full version picker later (host multiple
> `firmware-X.Y.Z.bin` + a manifest); the single-file layout above is the
> minimal "Install latest" (Level A) setup.
