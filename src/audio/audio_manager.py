"""Audio manager for handling sound effects and ambient audio"""

import pygame
import os

class AudioManager:
    def __init__(self):
        """Initialize the audio manager"""
        # Initialize pygame mixer
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()

        # Audio channels
        self.ambient_channel = pygame.mixer.Channel(0)
        self.music_channel = pygame.mixer.Channel(1)
        self.sfx_channel = pygame.mixer.Channel(2)

        # Loaded sounds
        self.sounds = {}
        self.ambient_sound = None
        self.music_sound = None

        # Volume settings
        self.master_volume = 0.7
        self.ambient_volume = 0.6
        self.music_volume = 0.5
        self.sfx_volume = 0.8

        # Mute state
        self.is_muted = False
        self.previous_volume = self.master_volume

        print("Audio manager initialized")

    def load_sound(self, name, file_path):
        """Load a sound file"""
        try:
            # Get absolute path
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            full_path = os.path.join(project_root, file_path)

            if os.path.exists(full_path):
                sound = pygame.mixer.Sound(full_path)
                self.sounds[name] = sound
                print(f"Loaded sound: {name} from {file_path}")
                return True
            else:
                print(f"Sound file not found: {full_path}")
                return False
        except Exception as e:
            print(f"Error loading sound {name}: {e}")
            return False

    def play_ambient(self, sound_name, loop=True, fade_in_ms=2000):
        """Play ambient sound with optional fade in"""
        if sound_name in self.sounds:
            try:
                # Stop current ambient if playing
                self.stop_ambient()

                # Set volume
                sound = self.sounds[sound_name]
                sound.set_volume(self.ambient_volume * self.master_volume)

                # Play with fade in
                if fade_in_ms > 0:
                    self.ambient_channel.play(sound, loops=-1 if loop else 0, fade_ms=fade_in_ms)
                else:
                    self.ambient_channel.play(sound, loops=-1 if loop else 0)

                self.ambient_sound = sound_name
                print(f"Playing ambient sound: {sound_name}")
                return True
            except Exception as e:
                print(f"Error playing ambient sound {sound_name}: {e}")
                return False
        else:
            print(f"Ambient sound not found: {sound_name}")
            return False

    def play_music(self, sound_name, loop=True, fade_in_ms=2000):
        """Play background music with optional fade in"""
        if sound_name in self.sounds:
            try:
                # Stop current music if playing
                self.stop_music()

                # Set volume
                sound = self.sounds[sound_name]
                sound.set_volume(self.music_volume * self.master_volume)

                # Play with fade in
                if fade_in_ms > 0:
                    self.music_channel.play(sound, loops=-1 if loop else 0, fade_ms=fade_in_ms)
                else:
                    self.music_channel.play(sound, loops=-1 if loop else 0)

                self.music_sound = sound_name
                print(f"Playing background music: {sound_name}")
                return True
            except Exception as e:
                print(f"Error playing background music {sound_name}: {e}")
                return False
        else:
            print(f"Background music not found: {sound_name}")
            return False

    def play_sfx(self, sound_name, volume=1.0):
        """Play a sound effect"""
        if sound_name in self.sounds:
            try:
                sound = self.sounds[sound_name]
                sound.set_volume(self.sfx_volume * self.master_volume * volume)
                self.sfx_channel.play(sound)
                return True
            except Exception as e:
                print(f"Error playing SFX {sound_name}: {e}")
                return False
        else:
            print(f"SFX sound not found: {sound_name}")
            return False

    def stop_ambient(self, fade_out_ms=1000):
        """Stop ambient sound with optional fade out"""
        if self.ambient_channel.get_busy():
            if fade_out_ms > 0:
                self.ambient_channel.fadeout(fade_out_ms)
            else:
                self.ambient_channel.stop()
            self.ambient_sound = None

    def stop_music(self, fade_out_ms=1000):
        """Stop background music with optional fade out"""
        if self.music_channel.get_busy():
            if fade_out_ms > 0:
                self.music_channel.fadeout(fade_out_ms)
            else:
                self.music_channel.stop()
            self.music_sound = None

    def set_master_volume(self, volume):
        """Set master volume (0.0 to 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        # Update current playing sounds
        if self.ambient_sound and self.ambient_sound in self.sounds:
            self.sounds[self.ambient_sound].set_volume(self.ambient_volume * self.master_volume)
        if self.music_sound and self.music_sound in self.sounds:
            self.sounds[self.music_sound].set_volume(self.music_volume * self.master_volume)

    def set_ambient_volume(self, volume):
        """Set ambient volume (0.0 to 1.0)"""
        self.ambient_volume = max(0.0, min(1.0, volume))
        # Update current ambient sound
        if self.ambient_sound and self.ambient_sound in self.sounds:
            self.sounds[self.ambient_sound].set_volume(self.ambient_volume * self.master_volume)

    def set_music_volume(self, volume):
        """Set background music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        # Update current music
        if self.music_sound and self.music_sound in self.sounds:
            self.sounds[self.music_sound].set_volume(self.music_volume * self.master_volume)

    def set_sfx_volume(self, volume):
        """Set SFX volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))

    def toggle_mute(self):
        """Toggle mute state for all audio"""
        if self.is_muted:
            # Unmute
            self.is_muted = False
            self.set_master_volume(self.previous_volume)
            print("Audio unmuted")
        else:
            # Mute
            self.is_muted = True
            self.previous_volume = self.master_volume
            self.set_master_volume(0.0)
            print("Audio muted")

    def is_muted_state(self):
        """Check if audio is muted"""
        return self.is_muted

    def is_ambient_playing(self):
        """Check if ambient sound is currently playing"""
        return self.ambient_channel.get_busy()

    def is_music_playing(self):
        """Check if background music is currently playing"""
        return self.music_channel.get_busy()

    def cleanup(self):
        """Clean up audio resources"""
        pygame.mixer.quit()

    def load_ambient_pack(self):
        """Load common ambient sounds and background music"""
        ambient_sounds = [
            ("forest_rain", "assets/audio/ambience/forest_rain_distant_thunder_loopable.mp3"),
        ]

        music_sounds = [
            ("forest_rain_music", "assets/audio/ambience/forest_rain_distant_thunder_loopable.wav"),
        ]

        for name, path in ambient_sounds:
            self.load_sound(name, path)

        for name, path in music_sounds:
            self.load_sound(name, path)