import argparse
from edgetpu.detection.engine import DetectionEngine
import picamera
import io

from DetectionThread import DetectionThread
from CameraCaptureThread import CameraCaptureThread 
from DrawThread import DrawThread

FULL_SIZE_W = 640
FULL_SIZE_H = 480

CAMERA_MULTIPLE = (16, 32)

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

    stream = io.BytesIO()
    with picamera.PiCamera() as camera:
        camera.resolution = (FULL_SIZE_W, FULL_SIZE_H)
        camera.framerate = 30

        camera.start_preview(fullscreen=False, window=(700, 200, FULL_SIZE_W,FULL_SIZE_H))
        valid_resize_w = width - width%CAMERA_MULTIPLE[1]
        valid_resize_h = height - height%CAMERA_MULTIPLE[0]

        camera_capture_thread = CameraCaptureThread(stream, width, height).start()

        detection_thread = DetectionThread(engine, camera_capture_thread, args.label).start()

        draw_thread = DrawThread(detection_thread, camera).start()

        for cap in camera.capture_continuous(stream,
              format='rgb',
              #  format='jpeg',
              use_video_port=True,
              resize=(valid_resize_w, valid_resize_h)):

            stream.truncate()
            stream.seek(0)


      #  if detected_boxes is not None:
          #  print(detected_boxes)

if __name__ == '__main__':
    main()
