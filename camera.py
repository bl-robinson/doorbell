import picamera
import os
import datetime as dt
import pyshine as ps
import threading
import time

_base_path = "/var/log/doorbell"

HTML="""
<html>
<head>
<title>Front Door</title>
</head>

<body>
<center><img src="stream.mjpg" width='1920' height='1080' autoplay playsinline></center>
</body>
</html>
"""

class Cam():
    stdin_path = "/dev/null"
    stdout_path = os.path.join(_base_path, "sec_cam.out") # Can also be /dev/null
    stderr_path =  os.path.join(_base_path, "sec_cam.err") # Can also be /dev/null
    pidfile_path =  os.path.join(_base_path, "sec_cam.pid")
    pidfile_timeout = 3

    def __init__(self):
        StreamProps = ps.StreamProps
        StreamProps.set_Page(StreamProps,HTML)
        StreamProps.set_Mode(StreamProps,'picamera')

        self.output_stream = ps.StreamOut()

        StreamProps.set_Output(StreamProps, self.output_stream)

        address = ('0.0.0.0',9000)

        self.file_string = "/mnt/doorbell/%s.h264"
        self.cam = picamera.PiCamera()
        self.cam.framerate = 10
        self.cam.resolution = (1280, 720)
        self.cam.hflip = True
        self.cam.vflip = True
        self.cam.annotate_background = picamera.Color('black')
        self.cam.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.server = ps.Streamer(address,StreamProps)
        self.server_thread = threading.Thread(None, self.server.serve_forever)
        self.annotate_thread = threading.Thread(None, self.annotate)
        self.stopped = False

    def annotate(self):
        while True and not self.stopped:
            time.sleep(1)
            self.cam.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def run(self):
        try:
            start_time = dt.datetime.now()
            print("Started WebServer")
            self.server_thread.start()
            self.annotate_thread.start()

            self.cam.start_recording(self.file_string % start_time.strftime('%Y-%m-%d--%H:%M:%S'), splitter_port=1)
            self.cam.start_recording(self.output_stream, splitter_port=2, format='mjpeg')

            while True:
                self.cam.wait_recording(900)
                self.cam.split_recording(self.file_string % dt.datetime.now().strftime('%Y-%m-%d--%H:%M:%S'), splitter_port=1)

        except(SystemExit, KeyboardInterrupt):
            self.stopped = True
        except:
            raise
        finally:
            self.server.shutdown()
            self.server_thread.join()
            self.annotate_thread.join()
            self.cam.stop_recording()
            print("Shutting Down")


def main():
    cam = Cam()
    cam.run()

if __name__ == '__main__':
    main()