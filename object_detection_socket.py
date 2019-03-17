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
import socket
import io
import time
import numpy as np
from PIL import Image
from PIL import ImageDraw


TCP_IP = '192.168.2.183'
UDP_IP = '192.168.2.183'
#  TCP_IP = '10.0.0.1'
UDP_PORT = 7000
TCP_PORT = 7000
#  BUFFER_SIZE = 1024

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

  print('opening socket.')

  #  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  #  s.bind((TCP_IP, TCP_PORT))
  #  s.listen(1)
  s.bind((UDP_IP, UDP_PORT))

  print('listening...')

  #  conn, addr = s.accept()

  #  print('accepted connection', addr)
  
  _, width, height, channels = engine.get_input_tensor_shape()


  imageSize = width*height*3

  receivedBytes = bytearray()


  start_s = time.time()
  # Open image.
  while 1:
    #  print('waiting')

    #  data = conn.recv(66507)

    data, addr = s.recvfrom(66507)

    receivedBytes+= data

    if (len(receivedBytes) > imageSize):

      input = np.frombuffer(receivedBytes[:imageSize], dtype=np.uint8)

      results = engine.DetectWithInputTensor(input, threshold=0.25,
                       top_k=10)
 
      print((time.time() - start_s) * 1000)

      start_s = time.time()
      receivedBytes=bytearray()
      
    
    #  start_s = time.time()

    # Run inference.
    #  results = engine.DetectWithInputTensor(input, threshold=0.25,
                       #  top_k=10)
    #  elapsed_s = time.time() - start_s

    #  boxes = scale_boxes(results, (width, height))

    #  conn.send(boxes)
 
  #  conn.close()


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

# Function to read labels from text files.
def ReadLabelFile(file_path):
  with open(file_path, 'r') as f:
    lines = f.readlines()
  ret = {}
  for line in lines:
    pair = line.strip().split(maxsplit=1)
    ret[int(pair[0])] = pair[1].strip()
  return ret

if __name__ == '__main__':
  main()
