"""A demo for object detection.

For Raspberry Pi, you need to install 'feh' as image viewer:
sudo apt-get install feh

Example (Running under python-tflite-source/edgetpu directory):

  - Face detection:
    python3.5 demo/object_detection.py \
    --model='test_data/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite' \
    --input='test_data/face.jpg'

  - Pet detection:
    python3.5 demo/object_detection.py \
    --model='test_data/ssd_mobilenet_v1_fine_tuned_edgetpu.tflite' \
    --label='test_data/pet_labels.txt' \
    --input='test_data/pets.jpg'

'--output' is an optional flag to specify file name of output image.
"""
import argparse
import platform
import subprocess
from edgetpu.detection.engine import DetectionEngine
import picamera
import io
import time
import numpy as np
from PIL import Image
from PIL import ImageDraw


# Function to read labels from text files.
def ReadLabelFile(file_path):
  with open(file_path, 'r') as f:
    lines = f.readlines()
  ret = {}
  for line in lines:
    pair = line.strip().split(maxsplit=1)
    ret[int(pair[0])] = pair[1].strip()
  return ret



def main():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--model', help='Path of the detection model.', required=True)
  args = parser.parse_args()

  renderer = None

  # Initialize engine.
  engine = DetectionEngine(args.model)

  shown = False

  frames = 0
  start_seconds = time.time()

  img = Image.new('RGBA', (640, 480))
  draw = ImageDraw.Draw(img)

  full_size_w = 640
  full_size_h = 480

  # Open image.
  with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.framerate = 30
    _, width, height, channels = engine.get_input_tensor_shape()
    
    print('input dims', width, height)
    camera.start_preview(fullscreen=False, window=(700, 200, 640,480))
    #  camera.start_preview()

    valid_resize_w = width - width%32

    try:
      stream = io.BytesIO()
      for foo in camera.capture_continuous(stream,
              format='rgb',
              #  format='jpeg',
              use_video_port=True,
              resize=(width, height)):
        stream.truncate()
        stream.seek(0)
        start_frame = time.time()
        input = np.frombuffer(stream.getvalue(), dtype=np.uint8)
        flattened = input

       
        start_s = time.time()

        # Run inference.
        ans = engine.DetectWithInputTensor(flattened, threshold=0.01,
                       top_k=10)

        elapsed_s = time.time() - start_frame

        img.putalpha(0)
        draw_boxes(draw, ans, (640, 480))

        imbytes = img.tobytes()
        if renderer == None:
          renderer = camera.add_overlay(imbytes, size=img.size, layer=4, format='rgba', fullscreen=False,window=(700, 200, 640, 480))
        else:
          renderer.update(imbytes)
 
        fps = frames * 1.0 / (time.time() - start_seconds)
        frames = frames + 1

        camera.annotate_text = "%.2fms, %d fps" % (elapsed_s * 1000.0, fps)
  
    finally:
      camera.stop_preview()

def draw_boxes(draw, answers, original_size):
  for obj in answers:
    full_scaled = obj.bounding_box * original_size 
    draw.rectangle(full_scaled.flatten().tolist(), outline='red')

def print_results(ans):
  for obj in ans:
    print ('-----------------------------------------')
    print ('score = ', obj.score)
    box = obj.bounding_box.flatten().tolist()
    print ('box = ', box)


if __name__ == '__main__':
  main()
