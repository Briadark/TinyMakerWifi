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

## Each release (automated)

Since 0.11.0 the whole flow is one script (run from the repo root, with
`FIRMWARE_VERSION` already bumped in **both** envs of `platformio.ini` and the
release commit in place):

```
%USERPROFILE%\.platformio\penv\Scripts\python.exe scripts\release.py --notes-file notes.md
```

It builds both envs, pushes `main` + the `vX.Y.Z` tag, publishes to `gh-pages`
(`firmware.bin`, `firmware-X.Y.Z.bin`, `version.txt`, `versions.txt`) and
creates the GitHub Release with `firmware.bin` + `firmware-full.bin` attached.
`--dry-run` stops after the build; the GitHub token comes from the git
credential helper automatically.

## Files on `gh-pages` (Level B - version picker)

- `version.txt` — two lines: latest version + firmware.bin URL (the printer's
  "Install latest" check).
- `firmware.bin` — always the latest build.
- `firmware-X.Y.Z.bin` — one archived copy per release; the dashboard's
  version picker installs these directly.
- `versions.txt` — the picker's manifest: one `X.Y.Z` per line, newest first.
  The browser fetches it straight from GitHub Pages (CORS is open).

The version check compares `MAJOR.MINOR.PATCH`, so "Install" only lights up when
`version.txt` is strictly newer than the running firmware. The dashboard's
picker also allows downgrades (with a warning).
