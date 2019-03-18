from threading import Thread, get_ident
from lib import pad_and_flatten, translate_and_scale_boxes, scale_boxes
import io
import picamera
import numpy as np
import time

FULL_SIZE_W = 640
FULL_SIZE_H = 480

# rasberry pi requires images to be resizes to multiples of 32x16
CAMERA_MULTIPLE = (16, 32)

class CameraCaptureThread:
    def __init__(self, tensor_width, tensor_height):
        self.tensor_width = tensor_width
        self.tensor_height = tensor_height

        self.valid_resize_w = tensor_width - tensor_width%CAMERA_MULTIPLE[1]
        self.valid_resize_h = tensor_height - tensor_height%CAMERA_MULTIPLE[0]

        self.padding_w = (tensor_width - self.valid_resize_w)//2
        self.padding_h = (tensor_height - self.valid_resize_h)//2

        self.frame = None
        self.frame_time = time.time()

    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()

        return self

    def update(self):
        with picamera.PiCamera() as camera:
            camera.resolution = (FULL_SIZE_W, FULL_SIZE_H)
            camera.framerate = 30

            camera.start_preview(fullscreen=False, window=(700, 200, FULL_SIZE_W,FULL_SIZE_H))
 
            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream,
                  format='rgb',
                  #  format='jpeg',
                  use_video_port=True,
                  resize=(self.valid_resize_w, self.valid_resize_h)):
                self.frame_time = time.time()
                stream.truncate()
                stream.seek(0)

                input = np.frombuffer(stream.getvalue(), dtype=np.uint8)
                
                if self.padding_w > 0 or self.padding_h > 0:
                    self.frame = pad_and_flatten(input, \
                            (self.valid_resize_h, self.valid_resize_w), \
                            self.padding_h, self.padding_w)
                else:
                    self.frame = input

    def read(self):
        return (self.frame, self.frame_time)

    def boxes_to_original_size(self, detection_results):
        if self.padding_w > 0 or self.padding_h > 0:
            return translate_and_scale_boxes(\
                  detection_results, \
                  (self.valid_resize_w, self.valid_resize_h),\
                  (self.padding_w, self.padding_h), \
                  (FULL_SIZE_W, FULL_SIZE_H))
        else:
          return scale_boxes(detection_results, (FULL_SIZE_W, FULL_SIZE_H))
