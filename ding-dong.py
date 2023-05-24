import time
import os
from homeassistant_api import Client
import logging
import sys

from signal import pause
from gpiozero import Button

logging.basicConfig()
logger = logging.getLogger('doorbell-button')
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.setLevel(logging.INFO)

API_TOKEN = os.getenv('HOME_ASSISTANT_TOKEN')
API_URL = "https://home-assistant.blrobinson.uk/api"

def button_pressed():
    logger.info("Ding dong ding dong")
    ring_doorbell()

def button_released():
    logger.info("Stop")

def main():
    button = Button(21)
    button.when_pressed = button_pressed
    button.when_released = button_released
    pause()

def ring_doorbell():
    with Client(
        API_URL, API_TOKEN, cache_session=False
    ) as client:
        media_player = client.get_domain("media_player")
        bedroom_speaker = client.get_entity(slug="bedroom_speaker", group_id="media_player")

        media_player.turn_on(entity_id=bedroom_speaker.entity_id)
        bedroom_speaker = client.get_entity(slug="bedroom_speaker", group_id="media_player")

        while bedroom_speaker.state.state == "off":
            bedroom_speaker = client.get_entity(slug="bedroom_speaker", group_id="media_player")
            time.sleep(0.1)

        starting_volume = bedroom_speaker.state.attributes['volume_level']
        logger.info("Setting Volume to the Max")
        media_player.volume_set(
            entity_id=bedroom_speaker.entity_id,
            volume_level=1
        )
        logger.info("Playing Doorbell")
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
        logger.info(f"Reset Volume to: {starting_volume}")
        media_player.volume_set(
            entity_id=bedroom_speaker.entity_id,
            volume_level=starting_volume
        )
        media_player.turn_off(entity_id=bedroom_speaker.entity_id)

if __name__ == "__main__":
    main()
