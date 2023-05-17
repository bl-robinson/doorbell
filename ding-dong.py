import time
import os
from homeassistant_api import Client

from signal import pause
# from gpiozero import Button

API_TOKEN = os.getenv('HOME_ASSISTANT_TOKEN')
API_URL = "https://home-assistant.blrobinson.uk/api"

def button_pressed():
    print("Ding dong ding dong")
    print("==========================")

def button_released():
    print("Stop")
    print("++++++++++++++++++++++++++")



def main():
    button = Button(21)
    button.when_pressed = button_pressed
    button.when_released = button_released
    pause()

def test_api():
    with Client(
        API_URL, API_TOKEN
    ) as client:
        bedroom_speaker = client.get_entity(slug="bedroom_speaker", group_id="media_player")
        print(bedroom_speaker)
        media_player = client.get_domain("media_player")
        print(media_player.play_media(entity_id="media_player.bedroom_speaker", media_content_id="mixkit-bell-ring-buzzer-2962.wav"))

if __name__ == "__main__":
    test_api()
