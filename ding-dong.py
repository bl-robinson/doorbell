import time
import os
from homeassistant_api import Client
import logging
import sys
import picamera
import paramiko

from datetime import datetime
from signal import pause
from gpiozero import Button

logging.basicConfig()
logger = logging.getLogger('doorbell-button')
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.setLevel(logging.INFO)

API_TOKEN = os.getenv('HOME_ASSISTANT_TOKEN')
API_URL = os.getenv('HOME_ASSISTANT_API_URL')
IMAGE_DESTINATION = os.getenv("UPLOAD_IMAGE_HOSTNAME")
IMAGE_PORT = os.getenv("UPLOAD_IMAGE_PORT")
IMAGE_DESTINATION_PATH = os.getenv("UPLOAD_IMAGE_DESTINATION_PATH")

def button_pressed():
    logger.info("Ding dong ding dong")
    ring_doorbell()
    photo_path = take_photo()
    send_notification(photo_path)

def button_released():
    logger.info("Stop")

def main():
    button = Button(21)
    button.when_pressed = button_pressed
    button.when_released = button_released
    pause()

def take_photo():
    with picamera.PiCamera() as camera:
        now = datetime.now()
        filename = now.strftime("%Y-%m-%d_%H-%M-%S.jpeg")
        camera.resolution = (1920, 1080)
        logger.info(f"Capturing image to {os.getcwd()}{filename}.jpeg")
        camera.capture(filename, splitter_port=3, format='jpeg')

    return f"{os.getcwd()}{filename}.jpeg"

def send_notification(photo_file):
    ssh = paramiko.SSHClient()
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(IMAGE_DESTINATION, port=IMAGE_PORT, key_filename="~/.ssh/id_rsa")
    sftp = ssh.open_sftp()
    sftp.put(photo_file, IMAGE_DESTINATION_PATH)
    sftp.close()
    ssh.close()
    logger.info(f"Image Avaliable at https://grabs.blrobinson.uk/images/grabs/{photo_file}")

def ring_doorbell():
    with Client(
        API_URL, API_TOKEN, cache_session=False
    ) as client:
        media_player = client.get_domain("media_player")

        alexa = client.get_entity(slug="ben_s_echo_dot", group_id="media_player")
        bedroom_speaker = client.get_entity(slug="bedroom_speaker", group_id="media_player")

        logger.info("Turning Speakers On")
        media_player.turn_on(entity_id=alexa.entity_id)
        media_player.turn_on(entity_id=bedroom_speaker.entity_id)

        alexa = client.get_entity(slug="ben_s_echo_dot", group_id="media_player")
        bedroom_speaker = client.get_entity(slug="bedroom_speaker", group_id="media_player")

        while bedroom_speaker.state.state == "off" or alexa.state.state == "off":
            bedroom_speaker = client.get_entity(slug="bedroom_speaker", group_id="media_player")
            alexa = client.get_entity(slug="ben_s_echo_dot", group_id="media_player")
            time.sleep(0.1)
            logger.warn("Waiting for speakers to turn on")

        starting_volume_bedroom = bedroom_speaker.state.attributes['volume_level']
        starting_volume_alexa = alexa.state.attributes['volume_level']

        logger.info("Setting Volume to the Max")
        media_player.volume_set(
            entity_id=bedroom_speaker.entity_id,
            volume_level=1
        )
        media_player.volume_set(
            entity_id=alexa.entity_id,
            volume_level=1
        )

        logger.info("Playing Doorbell")
        media_player.play_media(
            entity_id=bedroom_speaker.entity_id,
            media_content_id="media-source://media_source/local/doorbell-1.mp3",
            media_content_type="music",
        )
        media_player.play_media(
            entity_id=alexa.entity_id,
            media_content_id="amzn_sfx_doorbell_chime_01",
            media_content_type="sound"
        )
        time.sleep(2)
        media_player.play_media(
            entity_id=bedroom_speaker.entity_id,
            media_content_id="media-source://media_source/local/doorbell-1.mp3",
            media_content_type="music",
        )
        media_player.play_media(
            entity_id=alexa.entity_id,
            media_content_id="amzn_sfx_doorbell_chime_01",
            media_content_type="sound"
        )
        time.sleep(2)

        logger.info(f"Reset Volume")
        media_player.volume_set(
            entity_id=bedroom_speaker.entity_id,
            volume_level=starting_volume_bedroom
        )
        media_player.volume_set(
            entity_id=alexa.entity_id,
            volume_level=starting_volume_alexa
        )


        logger.info("Turning Speakers off")
        media_player.turn_off(entity_id=bedroom_speaker.entity_id)
        media_player.turn_off(entity_id=alexa.entity_id)

if __name__ == "__main__":
    main()
