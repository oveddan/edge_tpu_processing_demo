import argparse
import platform
import subprocess
from edgetpu.detection.engine import DetectionEngine
import picamera
import io
import time
import numpy as np
#  from PIL import Image
#  from PIL import ImageDraw
#  from lib import draw_labels, draw_boxes, read_label_file, pad_and_flatten, translate_and_scale_boxes, scale_boxes

def main():
  parser = argparse.ArgumentParser()
  #  parser.add_argument(
      #  '--model', help='Path of the detection model.', required=True)
  #  parser.add_argument(
      #  '--draw', help='If to draw the results.', default=True)
  #  parser.add_argument(
      #  '--label', help='Path of the labels file.')
  args = parser.parse_args()

  renderer = None

  # Initialize engine.
  #  engine = DetectionEngine(args.model)
  #  labels = read_label_file(args.label) if args.label else None

  shown = False

  frames = 0
  start_seconds = time.time()

  FULL_SIZE_W = 640
  FULL_SIZE_H = 480

  #  img = Image.new('RGBA', (FULL_SIZE_W, FULL_SIZE_H))
  #  draw = ImageDraw.Draw(img)

  # Open image.
  with picamera.PiCamera() as camera:
    camera.resolution = (FULL_SIZE_W, FULL_SIZE_H)
    camera.framerate = 30
    _, width, height, channels = engine.get_input_tensor_shape()
    
    print('input dims', width, height)
    camera.start_preview(fullscreen=False, window=(700, 200, FULL_SIZE_W,FULL_SIZE_H))
    #  camera.start_preview()

    # rasberry pi requires images to be resizes to multiples of 32x16
    camera_multiple = (16, 32)

    valid_resize_w = width - width%camera_multiple[1]
    valid_resize_h = height - height%camera_multiple[0]

    padding_w = (width - valid_resize_w)//2
    padding_h = (height - valid_resize_h)//2

    scale_w = FULL_SIZE_W / width
    scale_h = FULL_SIZE_H / height

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

        img = Image.fromarray(input, dtype=int
        with io.BytesIO() as output:


        tesIO() as output:
                image.save(output, format="GIF")
                    contents = output.getvalue()with 
        
        #  if padding_w > 0 or padding_h > 0:
          #  flattened = pad_and_flatten(input, (valid_resize_h, valid_resize_w), padding_h, padding_w)
        #  else:
          #  flattened = input

        #  # flatten padded element
        #  reshape_time = time.time() - start_frame
                
        #  start_s = time.time()

        #  # Run inference.
        #  results = engine.DetectWithInputTensor(flattened, threshold=0.25,
                       #  top_k=10)
        #  elapsed_s = time.time() - start_frame

        #  if padding_w > 0 or padding_h > 0:
          #  boxes = translate_and_scale_boxes(\
                  #  results, \
                  #  (valid_resize_w, valid_resize_h),\
                  #  (padding_w, padding_h), \
                  #  (FULL_SIZE_W, FULL_SIZE_H))
        #  else:
          #  boxes = scale_boxes(results, (FULL_SIZE_W, FULL_SIZE_H))

        #  if args.draw:
          #  img.putalpha(0)
          #  draw_boxes(draw, boxes)
          #  if labels:
            #  draw_labels(draw, results, boxes, labels)
          #  #  display_results(ans, labels, img)
          #  imbytes = img.tobytes()
          #  if renderer == None:
            #  renderer = camera.add_overlay(imbytes, size=img.size, layer=4, format='rgba', fullscreen=False,window=(700, 200, 640, FULL_SIZE_H))
          #  else:
            #  #  print('updating')
            #  renderer.update(imbytes)
 
        #  frame_seconds = time.time()
        #  #  print(frame_seconds - start_seconds, frames)
        #  fps = frames * 1.0 / (frame_seconds - start_seconds)
        #  frames = frames + 1

        #  time.sleep(1)
        camera.annotate_text = "%.2fms, %d fps" % (elapsed_s * 1000.0, fps)
  
    finally:
      camera.stop_preview()


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
