import pygame
import os
from mutagen.easyid3 import EasyID3

class MusicPlayer:
    def __init__(self, music_folder):
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.start_time = 0

        for file in os.listdir(music_folder):
            if file.endswith(".mp3") or file.endswith(".wav"):
                full_path = os.path.join(music_folder, file)

                # Try to get metadata
                title = file
                artist = "Unknown Artist"

                if file.endswith(".mp3"):
                    try:
                        audio = EasyID3(full_path)
                        title = audio.get("title", [file])[0]
                        artist = audio.get("artist", ["Unknown Artist"])[0]
                    except:
                        pass

                self.playlist.append({
                    "path": full_path,
                    "title": title,
                    "artist": artist
                })

        if not self.playlist:
            print("No music files found in folder!")

    def play(self):
        if self.playlist:
            pygame.mixer.music.load(self.playlist[self.current_index]["path"])
            pygame.mixer.music.play()
            self.is_playing = True
            self.start_time = pygame.time.get_ticks()

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self):
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.play()

    def prev_track(self):
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.play()

    def get_current_track_name(self):
        if self.playlist:
            track = self.playlist[self.current_index]
            return f"{track['artist']} - {track['title']}"
        return "No tracks loaded"

    def get_status(self):
        return "▶ Playing" if self.is_playing else "⏹ Stopped"
    
    def get_progress(self):
        if not self.playlist or not self.is_playing:
            return 0

        pos = pygame.mixer.music.get_pos()  # milliseconds
        if pos < 0:
            return 0

        return pos / 1000  # convert to seconds