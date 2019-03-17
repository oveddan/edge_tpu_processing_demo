from threading import Thread
from PiCamStream import PiCamStream 
from lib import read_label_file
from edgetpu.detection.engine import DetectionEngine
import time

class DetectionStream:
    def __init__(self, model_path, labels_path=None):
        #  print('loading model at', model_path, labels_path)
        self.engine = DetectionEngine(model_path)
        
        _, width, height, channels = self.engine.get_input_tensor_shape()

        self.width = width
        self.height = height

        if (labels_path is not None):
          self.labels = read_label_file(labels_path)
        else:
          self.labels = None

        self.picam_stream = PiCamStream(width, height).start()

        frame, frame_time = self.picam_stream.read()

        self.frame_time = frame_time

        if frame is not None:
            self.detect(frame)

        self.stopped = False
        self.detected_boxes = None
        self.detected_labels = None

    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()

        return self

    def update(self):
        while True:
            if self.stopped:
                return


            frame, frame_time = self.picam_stream.read()
            self.frame_time = frame_time

            if frame is not None:
                self.detect(frame)

    def read(self):
        return (self.detected_boxes, self.detected_labels)

    def detect(self, frame):
        start_s = time.time()
        results = self.engine.DetectWithInputTensor(frame, threshold=0.25,
                       top_k=10)
        print('inference time', (time.time()- start_s) * 1000)

        self.detected_boxes = self.picam_stream.boxes_to_original_size(results)

        if self.labels:
            self.detected_labels = list(map(lambda result: self.labels[result.label_id], results))
        else:
            self.detected_labels = None
   
        self.detection_time = time.time()
        print('time from frame read to detection', (self.detection_time - self.frame_time) * 1000) 

        return (self.detected_boxes, self.detected_labels)
