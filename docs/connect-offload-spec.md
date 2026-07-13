# TinyMaker Connect offload — spec draft

Status: **draft for discussion** (V. Sidlauskas, 2026-07-13). Goal agreed in the
team chat: Connect can grow as big as we like **on the server** while the
printer's flash footprint stays flat.

## Principle

The printer keeps a small, stable **LAN API**; the Connect **site** does all
browsing, managing and community UI, and talks to the printer the same way the
boot-animation "Send to printer" already does.

## What stays in firmware

| Piece | Why |
|---|---|
| Connect settings + registration (Settings tab) | needs NVS, secrets stay on-device |
| `POST /upload` (model import incl. `model.json` metadata args) | the site pushes models to the printer |
| `POST /api/boot-anim/install` | the site pushes animations |
| `GET /api/status`, `GET /api/files` (read-only) | lets the site show "already on SD / printing now" |
| Share-from-SD flow (SD manager → Details → Share) | reads layer PNGs off the SD, only the printer can do it |
| Connect tab, minimal: "Registered as X" + **Open TinyMaker Connect** link + model activity | one click into the site |

## What moves to the site

Model browsing, previews, ratings/bookmarks, "my shared models" management
(publish/hide/remove), boot-animation library, leaderboard, and any future
community features. None of these cost printer flash again.

## How the site reaches the printer

- The dashboard's **Open TinyMaker Connect** link opens
  `<connectBaseUrl>/?printer=<host>` so the site knows the printer's LAN
  address (user can correct it on the site; bookmarkable).
- The site calls the printer's LAN API from the browser (same-network), like
  the boot-anim install does today.

## Security rules

1. **CORS allowlist, not `*`**: printer answers cross-origin requests only for
   the configured `connectBaseUrl` origin (covers custom/self-hosted servers).
   Applies to every endpoint the site may call; includes `OPTIONS` preflight.
2. Existing gates stay: **Web control** off = LAN API mutating calls refuse;
   **busy** = 409 while printing.
3. **No secrets in URLs** — the publish token travels only in the
   `X-TinyMaker-Token` header (server change: stop reading it from the query).
4. The printer never proxies site content; the browser talks to both sides.

## Open question (for Brian)

"My shared models" management needs the publish token **on the site**. Today
the token lives in printer NVS and the dashboard hands it to the browser.
Site-centric options: (a) the site reads it from the printer's LAN API when the
user opens the site via the dashboard link (web-control gated), or (b) a proper
user session on the server (recovery-code claim). (b) is cleaner long-term;
(a) is zero-server-work. Pick one before the management UI moves.

## Migration

1. **0.15.0** (with the PR #10 feature half): Connect tab slimmed as agreed
   (Models + boot-anim install only), leaderboard = link to the site.
2. Site grows pages for boot-anim library + leaderboard (server work, no
   firmware release needed thanks to auto-update).
3. **0.16.x**: model browsing moves to the site; firmware Connect tab shrinks
   to "Registered as X + Open TinyMaker Connect + activity line". CORS
   allowlist + header-only token land here at the latest.
