import time
import os
from homeassistant_api import Client

from signal import pause
from gpiozero import Button

API_TOKEN = os.getenv('HOME_ASSISTANT_TOKEN')
API_URL = "https://home-assistant.blrobinson.uk/api"

def button_pressed():
    print("Ding dong ding dong")
    ring_doorbell()
    print("==========================")

def button_released():
    print("Stop")
    print("++++++++++++++++++++++++++")

def main():
    button = Button(21)
    button.when_pressed = button_pressed
    button.when_released = button_released
    pause()

def ring_doorbell():
    with Client(
        API_URL, API_TOKEN
    ) as client:
        media_player = client.get_domain("media_player")
        bedroom_speaker = client.get_entity(slug="bedroom_speaker", group_id="media_player")
        media_player.turn_on(entity_id=bedroom_speaker.entity_id)
        starting_volume = bedroom_speaker.state.attributes['volume_level']

        media_player.volume_set(
            entity_id=bedroom_speaker.entity_id,
            volume_level=1
        )
        media_player.play_media(
            entity_id=bedroom_speaker.entity_id,
            media_content_id="media-source://media_source/local/doorbell-1.mp3",
            media_content_type="music",
            # announce=True # Not supported by google cast yet currently will just stop current thing playing
        )
        time.sleep(2)
        media_player.play_media(
            entity_id=bedroom_speaker.entity_id,
            media_content_id="media-source://media_source/local/doorbell-1.mp3",
            media_content_type="music",
            # announce=True # Not supported by google cast yet currently will just stop current thing playing
        )
        time.sleep(2)
        media_player.volume_set(
            entity_id=bedroom_speaker.entity_id,
            volume_level=starting_volume
        )

if __name__ == "__main__":
    main()
