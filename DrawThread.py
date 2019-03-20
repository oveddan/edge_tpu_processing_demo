from PIL import Image, ImageDraw
from threading import Thread
from lib import draw_boxes, draw_text
import time

FULL_SIZE_W = 640
FULL_SIZE_H = 480

class DrawThread:
    def __init__(self, detection_thread, camera):
        self.detection_thread = detection_thread
        self.last_detection_time = None
        self.image = Image.new('RGBA', (FULL_SIZE_W, FULL_SIZE_H))
        self.renderer = camera.add_overlay(self.image.tobytes(), size=self.image.size, layer=4, format='rgba', fullscreen=False,window=(700, 200, 640, FULL_SIZE_H)) 


    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()

        return self

    def update(self):
        while True:
            boxes, labels, frame_time = self.detection_thread.read()

            if self.last_detection_time == frame_time:
                #  print('drawing sleeeping', frame_time)
                time.sleep(0.01)
            else:
                #  print('drawing')
                self.last_detection_time = frame_time

                self.draw(boxes, labels, frame_time)


    def draw(self, boxes, labels, frame_time):
        if boxes is not None:
            self.image.putalpha(0)
            draw = ImageDraw.Draw(self.image)
            draw_boxes(draw, boxes)
            if labels:
                draw_text(draw, labels, boxes)
            self.renderer.update(self.image.tobytes())
            print('time to draw from frame time', (time.time() - frame_time) * 1000)
        



