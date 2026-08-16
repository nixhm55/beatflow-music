"""
BeatFlow Music Player
A clean, functional music player for Android built with Kivy + KivyMD
"""

import os
import time
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty

# ── Android storage permission helper ──────────────────────────────────────────
def request_android_permissions():
    if platform == "android":
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.READ_MEDIA_AUDIO,
        ])

def get_music_dirs():
    """Return likely music folders depending on platform."""
    if platform == "android":
        return [
            "/sdcard/Music",
            "/sdcard/Download",
            "/storage/emulated/0/Music",
            "/storage/emulated/0/Download",
        ]
    # Desktop fallback for testing
    return [os.path.expanduser("~/Music"), os.path.expanduser("~/Downloads")]

# ── KV Layout ─────────────────────────────────────────────────────────────────
KV = """
#:import dp kivy.metrics.dp

<SongItem>:
    text: root.title
    secondary_text: root.artist
    on_release: app.play_song(root.path)
    IconLeftWidget:
        icon: "music-note"
        theme_text_color: "Custom"
        text_color: app.theme_cls.primary_color

MDScreenManager:
    PlayerScreen:
        name: "player"
    LibraryScreen:
        name: "library"

<PlayerScreen>:
    name: "player"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: app.theme_cls.bg_darkest

        # ── Top bar ──────────────────────────────────────────────────────────
        MDTopAppBar:
            title: "BeatFlow"
            left_action_items: [["menu", lambda x: app.go_library()]]
            right_action_items: [["magnify", lambda x: app.go_library()]]
            md_bg_color: app.theme_cls.primary_dark
            specific_text_color: 1,1,1,1

        # ── Album art placeholder ─────────────────────────────────────────────
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(24)
            spacing: dp(16)
            size_hint_y: 0.42

            MDCard:
                radius: [dp(20)]
                md_bg_color: 0.15, 0.15, 0.2, 1
                MDBoxLayout:
                    padding: dp(30)
                    MDIcon:
                        icon: "music-circle"
                        halign: "center"
                        font_size: dp(120)
                        theme_text_color: "Custom"
                        text_color: app.theme_cls.primary_light

        # ── Song info ────────────────────────────────────────────────────────
        MDBoxLayout:
            orientation: "vertical"
            padding: [dp(24), 0]
            spacing: dp(4)
            size_hint_y: 0.12

            MDLabel:
                id: title_label
                text: app.current_title
                font_style: "H6"
                halign: "center"
                theme_text_color: "Primary"
                shorten: True
                shorten_from: "right"

            MDLabel:
                id: artist_label
                text: app.current_artist
                font_style: "Caption"
                halign: "center"
                theme_text_color: "Secondary"

        # ── Seek bar ─────────────────────────────────────────────────────────
        MDBoxLayout:
            orientation: "vertical"
            padding: [dp(24), 0]
            spacing: dp(2)
            size_hint_y: 0.1

            MDSlider:
                id: seek_slider
                min: 0
                max: 100
                value: app.progress
                on_touch_up: app.seek(self.value)
                color: app.theme_cls.primary_color

            MDBoxLayout:
                MDLabel:
                    id: elapsed_label
                    text: app.elapsed_str
                    font_style: "Caption"
                    theme_text_color: "Secondary"
                    halign: "left"
                MDLabel:
                    id: duration_label
                    text: app.duration_str
                    font_style: "Caption"
                    theme_text_color: "Secondary"
                    halign: "right"

        # ── Controls ─────────────────────────────────────────────────────────
        MDBoxLayout:
            size_hint_y: 0.18
            padding: dp(16)
            spacing: dp(8)

            MDIconButton:
                icon: "shuffle"
                theme_text_color: "Custom"
                text_color: app.theme_cls.primary_light if app.shuffle else (0.5,0.5,0.5,1)
                on_release: app.toggle_shuffle()
                user_font_size: dp(28)

            MDIconButton:
                icon: "skip-previous"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                on_release: app.prev_song()
                user_font_size: dp(36)

            MDFloatingActionButton:
                icon: "pause" if app.playing else "play"
                md_bg_color: app.theme_cls.primary_color
                on_release: app.toggle_play()
                elevation: 4

            MDIconButton:
                icon: "skip-next"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                on_release: app.next_song()
                user_font_size: dp(36)

            MDIconButton:
                icon: "repeat" if not app.repeat_one else "repeat-once"
                theme_text_color: "Custom"
                text_color: app.theme_cls.primary_light if app.repeat else (0.5,0.5,0.5,1)
                on_release: app.toggle_repeat()
                user_font_size: dp(28)

        # ── Volume ───────────────────────────────────────────────────────────
        MDBoxLayout:
            padding: [dp(24), dp(8)]
            spacing: dp(8)
            size_hint_y: 0.08

            MDIcon:
                icon: "volume-low"
                theme_text_color: "Secondary"
                size_hint_x: None
                width: dp(32)

            MDSlider:
                id: vol_slider
                min: 0
                max: 1
                step: 0.01
                value: 0.8
                on_value: app.set_volume(self.value)
                color: app.theme_cls.primary_light

            MDIcon:
                icon: "volume-high"
                theme_text_color: "Secondary"
                size_hint_x: None
                width: dp(32)

<LibraryScreen>:
    name: "library"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: app.theme_cls.bg_darkest

        MDTopAppBar:
            title: "Library"
            left_action_items: [["arrow-left", lambda x: app.go_player()]]
            right_action_items: [["refresh", lambda x: app.scan_music()]]
            md_bg_color: app.theme_cls.primary_dark
            specific_text_color: 1,1,1,1

        MDLabel:
            id: lib_status
            text: app.lib_status
            halign: "center"
            theme_text_color: "Secondary"
            font_style: "Caption"
            size_hint_y: None
            height: dp(32)

        MDScrollView:
            MDList:
                id: song_list
"""

# ── Song list item ─────────────────────────────────────────────────────────────
class SongItem(TwoLineIconListItem):
    title  = StringProperty("")
    artist = StringProperty("Unknown Artist")
    path   = StringProperty("")

# ── Screens ───────────────────────────────────────────────────────────────────
class PlayerScreen(MDScreen):  pass
class LibraryScreen(MDScreen): pass

# ── App ───────────────────────────────────────────────────────────────────────
class BeatFlowApp(MDApp):

    # Observable state
    current_title = StringProperty("No song loaded")
    current_artist = StringProperty("Tap Library to browse")
    progress      = NumericProperty(0)
    elapsed_str   = StringProperty("0:00")
    duration_str  = StringProperty("0:00")
    playing       = BooleanProperty(False)
    shuffle       = BooleanProperty(False)
    repeat        = BooleanProperty(False)
    repeat_one    = BooleanProperty(False)
    lib_status    = StringProperty("Scanning…")
    songs         = ListProperty([])   # list of {"title","artist","path"}

    _sound       = None
    _volume      = 0.8
    _current_idx = -1
    _ticker      = None

    # ── App setup ─────────────────────────────────────────────────────────────
    def build(self):
        self.theme_cls.theme_style   = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        return Builder.load_string(KV)

    def on_start(self):
        request_android_permissions()
        Clock.schedule_once(lambda dt: self.scan_music(), 1)

    # ── Navigation ────────────────────────────────────────────────────────────
    def go_library(self):
        self.root.current = "library"

    def go_player(self):
        self.root.current = "player"

    # ── Music scanning ────────────────────────────────────────────────────────
    def scan_music(self):
        self.lib_status = "Scanning…"
        self.songs = []
        song_list = self.root.get_screen("library").ids.song_list
        song_list.clear_widgets()

        found = []
        for folder in get_music_dirs():
            if not os.path.isdir(folder):
                continue
            for root_dir, _, files in os.walk(folder):
                for f in files:
                    if f.lower().endswith((".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac")):
                        path  = os.path.join(root_dir, f)
                        title = os.path.splitext(f)[0]
                        found.append({"title": title, "artist": "Unknown Artist", "path": path})

        self.songs = found
        if not found:
            self.lib_status = "No music found — copy MP3s to /sdcard/Music"
        else:
            self.lib_status = f"{len(found)} songs found"
            for s in found:
                item = SongItem(title=s["title"], artist=s["artist"], path=s["path"])
                song_list.add_widget(item)

    # ── Playback ──────────────────────────────────────────────────────────────
    def play_song(self, path):
        """Load and play a song by file path."""
        self._stop_sound()
        sound = SoundLoader.load(path)
        if not sound:
            self.current_title  = "Error loading file"
            self.current_artist = path
            return

        # Update metadata display
        title = os.path.splitext(os.path.basename(path))[0]
        self.current_title  = title
        self.current_artist = "Unknown Artist"
        self.duration_str   = self._fmt(sound.length)

        # Find index in playlist
        paths = [s["path"] for s in self.songs]
        self._current_idx = paths.index(path) if path in paths else -1

        sound.volume   = self._volume
        sound.bind(on_stop=self._on_stop)
        sound.play()
        self._sound = sound
        self.playing = True

        if self._ticker:
            self._ticker.cancel()
        self._ticker = Clock.schedule_interval(self._update_progress, 0.5)

        self.go_player()

    def _stop_sound(self):
        if self._sound:
            self._sound.stop()
            self._sound.unload()
            self._sound = None
        if self._ticker:
            self._ticker.cancel()
            self._ticker = None
        self.playing  = False
        self.progress = 0
        self.elapsed_str = "0:00"

    def toggle_play(self):
        if not self._sound:
            if self.songs:
                self.play_song(self.songs[0]["path"])
            return
        if self.playing:
            self._sound.stop()
            self.playing = False
            if self._ticker:
                self._ticker.cancel()
        else:
            self._sound.play()
            self.playing = True
            self._ticker = Clock.schedule_interval(self._update_progress, 0.5)

    def next_song(self):
        if not self.songs:
            return
        if self.shuffle:
            import random
            idx = random.randint(0, len(self.songs) - 1)
        else:
            idx = (self._current_idx + 1) % len(self.songs)
        self.play_song(self.songs[idx]["path"])

    def prev_song(self):
        if not self.songs:
            return
        if self._sound and self._sound.get_pos() > 3:
            self._sound.seek(0)
            return
        if self.shuffle:
            import random
            idx = random.randint(0, len(self.songs) - 1)
        else:
            idx = (self._current_idx - 1) % len(self.songs)
        self.play_song(self.songs[idx]["path"])

    def seek(self, value):
        if self._sound and self._sound.length:
            pos = (value / 100.0) * self._sound.length
            self._sound.seek(pos)

    def set_volume(self, val):
        self._volume = val
        if self._sound:
            self._sound.volume = val

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle

    def toggle_repeat(self):
        if not self.repeat and not self.repeat_one:
            self.repeat = True
        elif self.repeat and not self.repeat_one:
            self.repeat_one = True
            self.repeat = False
        else:
            self.repeat_one = False
            self.repeat = False

    # ── Internal helpers ──────────────────────────────────────────────────────
    def _update_progress(self, dt):
        if self._sound and self._sound.length and self._sound.length > 0:
            pos = self._sound.get_pos()
            self.progress    = (pos / self._sound.length) * 100
            self.elapsed_str = self._fmt(pos)

    def _on_stop(self, instance):
        """Called when a track finishes naturally."""
        if self.repeat_one and self._sound:
            self._sound.seek(0)
            self._sound.play()
        else:
            self.next_song()

    @staticmethod
    def _fmt(secs):
        if secs is None or secs < 0:
            return "0:00"
        m = int(secs) // 60
        s = int(secs) % 60
        return f"{m}:{s:02d}"


if __name__ == "__main__":
    BeatFlowApp().run()
