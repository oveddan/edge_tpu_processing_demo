import numpy as np
import io

# Function to read labels from text files.
def read_label_file(file_path):
  with open(file_path, 'r') as f:
    lines = f.readlines()
  ret = {}
  for line in lines:
    pair = line.strip().split(maxsplit=1)
    ret[int(pair[0])] = pair[1].strip()
  return ret

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


