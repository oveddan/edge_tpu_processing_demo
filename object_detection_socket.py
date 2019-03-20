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
import json
from lib import read_label_file
from PIL import Image
from PIL import ImageDraw


#  UDP_IP = '192.168.2.183'
UDP_IP = '127.0.0.1'
TCP_IP = UDP_IP
#  TCP_IP = '10.0.0.1'
UDP_RECEIVE_PORT = 9100
UDP_SEND_PORT = 9101
TCP_PORT = 9101
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
  labels = read_label_file(args.label) if args.label else None

  shown = False

  frames = 0
  start_seconds = time.time()

  print('opening socket.')

  #  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  #  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  #  s.bind((TCP_IP, TCP_PORT))
  #  s.listen(1)
  #  senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  receiveSocket.bind((UDP_IP, UDP_RECEIVE_PORT))
  #  senderSocket.bind((UDP_IP, UDP_SEND_PORT))

  print('listening...')

  _, width, height, channels = engine.get_input_tensor_shape()

  imageSize = width*height*3


  print('waiting for client')

  #  conn, addr = s.accept()

  #  print('Connection address:', addr)
  # Open image.
  while 1:
    data, addr = receiveSocket.recvfrom(66507)

    if (len(data) > 0):
        start_s = time.time()

        try:
           image = Image.open(io.BytesIO(data)).convert('RGB')
        except OSError:
           print('Could not read image')
           continue

        input = np.frombuffer(image.tobytes(), dtype=np.uint8)

        results = engine.DetectWithInputTensor(input, threshold=0.25,
                       top_k=10)
     
        print('time to process image', (time.time() - start_s) * 1000)

        output = to_output(results, image.size, labels)
        
        message = json.dumps({'results': output}) + '|'

        #  print('sending', message)
        #  conn.send(message.encode('utf-8'))
        #  receiveSocket.sendto(message.encode('utf-8'), addr)
        senderSocket.sendto(message.encode('utf-8'), (UDP_IP, UDP_SEND_PORT))
      #  receivedBytes=bytearray()
      
    
    #  start_s = time.time()

    # Run inference.
    #  results = engine.DetectWithInputTensor(input, threshold=0.25,
                       #  top_k=10)
    #  elapsed_s = time.time() - start_s


 
  #  conn.close()

def to_output(results, full_size, labels):
    return list(map(lambda result: { \
            'box': scale_box(result.bounding_box, full_size),\
            'label': labels[result.label_id] if labels is not None else None
            }, results))

def scale_boxes(results, full_size):
    return list(map(lambda result: \
          (scale_box(result.bounding_box, full_size)).tolist(), results))

def to_label_texts(results, labels):
    if labels is None:
        return None
    else:
        return list(map(lambda result: labels[result.label_id], results))

def scale_box(box, full_size):
    return (box* (full_size[0], full_size[1])).flatten().tolist()

if __name__ == '__main__':
  main()
