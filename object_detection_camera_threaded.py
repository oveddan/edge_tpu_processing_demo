import argparse
from edgetpu.detection.engine import DetectionEngine

from DetectionThread import DetectionThread
from CameraCaptureThread import CameraCaptureThread 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
      '--model', help='Path of the detection model.', required=True)
    parser.add_argument(
      '--draw', help='If to draw the results.', default=True)
    parser.add_argument(
      '--label', help='Path of the labels file.')
    args = parser.parse_args()

    engine = DetectionEngine(args.model)
    _, width, height, channels = engine.get_input_tensor_shape()

    camera_capture_thread = CameraCaptureThread(width, height).start()

    detection_thread = DetectionThread(engine, camera_capture_thread, args.label).start()

    #  draw_thread = DrawThread(detection_thread)
    while True:
      (detected_boxes, detected_labels) = detection_thread.read()

      #  if detected_boxes is not None:
          #  print(detected_boxes)

if __name__ == '__main__':
    main()
