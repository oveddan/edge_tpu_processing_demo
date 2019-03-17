import argparse

from DetectionStream import DetectionStream

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
      '--model', help='Path of the detection model.', required=True)
    parser.add_argument(
      '--draw', help='If to draw the results.', default=True)
    parser.add_argument(
      '--label', help='Path of the labels file.')
    args = parser.parse_args()

    detection_stream = DetectionStream(args.model, args.label)

    detection_stream.start()

    while True:
      (detected_boxes, detected_labels) = detection_stream.read()

      #  if detected_boxes is not None:
          #  print(detected_boxes)

if __name__ == '__main__':
    main()
