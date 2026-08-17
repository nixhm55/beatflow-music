[app]

# App metadata
title = BeatFlow
package.name = beatflow
package.domain = org.nisam

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

# ── Dependencies ──────────────────────────────────────────────────────────────
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow==10.2.0

# ── Android target ────────────────────────────────────────────────────────────
android.minapi = 21
android.api = 33
android.ndk = 25b
android.sdk = 34

android.archs = arm64-v8a

# ── Permissions ───────────────────────────────────────────────────────────────
android.permissions = READ_EXTERNAL_STORAGE, READ_MEDIA_AUDIO, FOREGROUND_SERVICE

# ── App orientation ───────────────────────────────────────────────────────────
orientation = portrait

# ── Fullscreen ────────────────────────────────────────────────────────────────
fullscreen = 0

# ── Icon (optional — Buildozer will use default if missing) ───────────────────
# icon.filename = %(source.dir)s/icon.png

# ── Presplash ─────────────────────────────────────────────────────────────────
# presplash.filename = %(source.dir)s/presplash.png

[buildozer]

# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# Warn on root — set 0 to allow building as root in Colab
warn_on_root = 1
