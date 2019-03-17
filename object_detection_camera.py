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
  parser.add_argument(
      '--draw', help='If to draw the results.', default=True)
  parser.add_argument(
      '--label', help='Path of the labels file.')
  args = parser.parse_args()

  renderer = None

  # Initialize engine.
  engine = DetectionEngine(args.model)
  labels = ReadLabelFile(args.label) if args.label else None

  shown = False

  frames = 0
  start_seconds = time.time()

  full_size_w = 640
  full_size_h = 480

  img = Image.new('RGBA', (full_size_w, full_size_h))
  draw = ImageDraw.Draw(img)

  # Open image.
  with picamera.PiCamera() as camera:
    camera.resolution = (full_size_w, full_size_h)
    camera.framerate = 30
    _, width, height, channels = engine.get_input_tensor_shape()
    
    print('input dims', width, height)
    camera.start_preview(fullscreen=False, window=(700, 200, full_size_w,full_size_h))
    #  camera.start_preview()

    # rasberry pi requires images to be resizes to multiples of 32x16
    camera_multiple = (16, 32)

    valid_resize_w = width - width%camera_multiple[1]
    valid_resize_h = height - height%camera_multiple[0]

    padding_w = (width - valid_resize_w)//2
    padding_h = (height - valid_resize_h)//2

    scale_w = full_size_w / width
    scale_h = full_size_h / height

    try:
      stream = io.BytesIO()
      for foo in camera.capture_continuous(stream,
              format='rgb',
              #  format='jpeg',
              use_video_port=True,
              resize=(valid_resize_w, valid_resize_h)):
        stream.truncate()
        stream.seek(0)
        start_frame = time.time()

        input = np.frombuffer(stream.getvalue(), dtype=np.uint8)
        
        if padding_w > 0 or padding_h > 0:
          flattened = pad_and_flatten(input, (valid_resize_h, valid_resize_w), padding_h, padding_w)
        else:
          flattened = input

        # flatten padded element
        reshape_time = time.time() - start_frame
                
        start_s = time.time()

        # Run inference.
        results = engine.DetectWithInputTensor(flattened, threshold=0.25,
                       top_k=10)
        elapsed_s = time.time() - start_frame

        if padding_w > 0 or padding_h > 0:
          boxes = translate_and_scale_boxes(\
                  results, \
                  (valid_resize_w, valid_resize_h),\
                  (padding_w, padding_h), \
                  (full_size_w, full_size_h))
        else:
          boxes = scale_boxes(results, (full_size_w, full_size_h))

        if args.draw:
          img.putalpha(0)
          draw_boxes(draw, boxes)
          if labels:
            draw_text(draw, results, boxes, labels)
          #  display_results(ans, labels, img)
          imbytes = img.tobytes()
          if renderer == None:
            renderer = camera.add_overlay(imbytes, size=img.size, layer=4, format='rgba', fullscreen=False,window=(700, 200, 640, full_size_h))
          else:
            #  print('updating')
            renderer.update(imbytes)
 
        frame_seconds = time.time()
        #  print(frame_seconds - start_seconds, frames)
        fps = frames * 1.0 / (frame_seconds - start_seconds)
        frames = frames + 1

        #  time.sleep(1)
        camera.annotate_text = "%.2fms, %d fps" % (elapsed_s * 1000.0, fps)
  
    finally:
      camera.stop_preview()


def translate_and_scale_boxes(results, padded_size, padding, full_size):
  return list(map(lambda result: translate_and_scale(\
          result.bounding_box, padded_size, padding, full_size), results))

def translate_and_scale(box, padded_size,padding, full_size):
  scale = (full_size[0] / padded_size[0], full_size[1] / padded_size[1])
  return (box * padded_size + padding) * scale

def scale_boxes(results, full_size):
  return list(map(lambda result: result.bounding_box * (full_size[0], full_size[1]), results))

def pad_and_flatten(input, img_size, padding_h, padding_w):
  padded = np.pad(
               input.reshape((img_size[0], img_size[1], 3)),
               ((padding_h, padding_h), (padding_w, padding_w), (0, 0)),
               'constant')
  # flatten
  padded.shape = (padded.shape[0] * padded.shape[1] * padded.shape[2])
  return padded

def draw_boxes(draw, boxes):
  for box in boxes:
    draw.rectangle(box.flatten().tolist(), outline='red')

def draw_text(draw, results, boxes, labels):
  for i, result in enumerate(results):
    label = labels[result.label_id]
    box = boxes[i]
    draw.text((box[0][0], box[0][1]), label, fill='red')

def display_results(ans, labels, img):
  #  print('RESULTS:', time.time())
  draw = ImageDraw.Draw(img)
  for obj in ans:
    print ('-----------------------------------------')
    if labels:
      print(obj.label_id, labels[obj.label_id])
    print ('score = ', obj.score)
    box = obj.bounding_box.flatten().tolist()
    if(obj.score > 0.5):
      draw.rectangle(box, outline='red')
    print ('box = ', box)


if __name__ == '__main__':
  main()
