Simple Doorbell project

camera.py -> handles picamera and 24/7 recording to mount at /mnt/doorbell Plus a live video stream viewable at http:9000 on the host running the process.

ding-dong.py -> handles talking to home-assistant api server with 2 devices.
   - One google home speaker
   - One Alexa, working using https://github.com/custom-components/alexa_media_player

Triggered button press from GPIO 21 to make the Alexa and Google Home speaker make doorbell noises. Also sets volume high before ringing the doorbell and resets it afterwards.


