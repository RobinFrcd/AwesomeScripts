import os
import signal
import subprocess
from logging import getLogger
from typing import Optional, Set

import click
from pynput import keyboard
from pynput.keyboard import Key

from awesomescripts import tools
from awesomescripts.constants import MEDIAS_FOLDER

tools.set_logger()
LOGGER = getLogger(__name__)


def play_sound(file_path: str):
    """Play a sound file using paplay (PulseAudio)"""
    try:
        # Using subprocess.Popen to avoid blocking and prevent shell injection
        subprocess.Popen(
            ["paplay", file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except Exception as e:
        LOGGER.error(f"Failed to play sound: {e}")


def enable_mic():
    os.system("pactl set-source-mute @DEFAULT_SOURCE@ 0")


def disable_mic():
    os.system("pactl set-source-mute @DEFAULT_SOURCE@ 1")


def toggle_sound():
    LOGGER.info("Toggle Sound")
    os.system("pactl set-sink-mute @DEFAULT_SINK@ toggle")


def get_default_source() -> str:
    proc = subprocess.run(["pactl", "get-default-source"], capture_output=True)
    return proc.stdout.decode().strip()


class PushToTalk:
    def __init__(
        self,
        ptt_key: str,
        ppt_toggle_key: Optional[Set[str]] = None,
        sound_toggle_key: Optional[Set[str]] = None,
    ):
        self.ppt_toggle_key = ppt_toggle_key or set()
        self.sound_toggle_key = sound_toggle_key or set()
        self.ptt_key = ptt_key

        self.__pressed: Set[str] = set()
        self.__is_ptt_enabled: bool = True

    def toggle_ptt(self):
        play_sound(os.path.join(MEDIAS_FOLDER, "snap.wav"))
        if self.__is_ptt_enabled:
            LOGGER.info("Disable PTT")
            enable_mic()
            self.__is_ptt_enabled = False
        else:
            LOGGER.info("Enable PTT")
            disable_mic()
            self.__is_ptt_enabled = True

    def on_press(self, key: Key):
        key_str = tools.get_key_str(key)
        self.__pressed.add(key_str)
        LOGGER.debug(f"on_press: {key_str}, pressed: {self.__pressed}")

        if self.__is_ptt_enabled and key_str == self.ptt_key:
            LOGGER.info(f"Enable mic with {key_str}")
            play_sound(os.path.join(MEDIAS_FOLDER, "button.wav"))
            enable_mic()

        if self.ppt_toggle_key and self.ppt_toggle_key.issubset(self.__pressed):
            self.toggle_ptt()
            # hard reset because pynput struggles with key combinations
            self.__pressed = set()

        if self.sound_toggle_key and self.sound_toggle_key.issubset(self.__pressed):
            toggle_sound()

    def on_release(self, key: Key):
        key_str = tools.get_key_str(key)
        LOGGER.debug(f"on_release: {key_str}")

        if self.__is_ptt_enabled and key_str == self.ptt_key:
            LOGGER.info(f"Disable mic with {key_str}")
            play_sound(os.path.join(MEDIAS_FOLDER, "button.wav"))
            disable_mic()

        self.__pressed.discard(key_str)

    def start_listener(self):
        signal.signal(signal.SIGINT, signal.default_int_handler)
        LOGGER.info(
            f"Start listening on {get_default_source()}. "
            f"PTT key: {self.ptt_key}, PTT Toggle: {self.ppt_toggle_key}, Mute Sound: {self.sound_toggle_key}"
        )
        try:
            disable_mic()

            with keyboard.Listener(
                on_press=self.on_press, on_release=self.on_release
            ) as listener:
                listener.join()
        finally:
            disable_mic()


@click.command()
@click.option("--ppt_key", help="Key name (eg. control_r).", required=True)
@click.option("--ppt_toggle_key", help="Key name (eg. control_r+!).", required=False)
@click.option("--sound_toggle_key", help="Key name (eg. control_r+m).", required=False)
def main(ppt_key: str, ppt_toggle_key: Optional[str], sound_toggle_key: Optional[str]):
    ppt_toggle_keys = set(ppt_toggle_key.split("+")) if ppt_toggle_key else set()
    sound_toggle_keys = set(sound_toggle_key.split("+")) if sound_toggle_key else set()
    ptt = PushToTalk(
        ppt_key, ppt_toggle_key=ppt_toggle_keys, sound_toggle_key=sound_toggle_keys
    )
    ptt.start_listener()


if __name__ == "__main__":
    main()
