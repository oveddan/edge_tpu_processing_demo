from threading import Thread, get_ident
from lib import read_label_file
from edgetpu.detection.engine import DetectionEngine
import time

class DetectionThread:
    def __init__(self, engine, camera_capture_thread, labels_path=None):
        self.engine = engine
        
        if (labels_path is not None):
          self.labels = read_label_file(labels_path)
        else:
          self.labels = None

        self.camera_capture_thread = camera_capture_thread
        self.frame_time = None
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
            frame, frame_time = self.camera_capture_thread.read()

            if frame is None or frame_time == self.frame_time:
                time.sleep(0.01)
            else:
                self.frame_time = frame_time

                self.detect(frame)

    def read(self):
        return (self.detected_boxes, self.detected_labels, self.frame_time)

    def detect(self, frame):
        start_s = time.time()
        results = self.engine.DetectWithInputTensor(frame, threshold=0.25,
                       top_k=10)
        print('inference time',  (time.time()- start_s) * 1000)

        self.detected_boxes = self.camera_capture_thread.boxes_to_original_size(results)

        if self.labels:
            self.detected_labels = list(map(lambda result: self.labels[result.label_id], results))
        else:
            self.detected_labels = None
   
        self.detection_time = time.time()
        print('time from frame read to detection', (self.detection_time - self.frame_time) * 1000) 

        return (self.detected_boxes, self.detected_labels)
