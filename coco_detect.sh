#!/bin/bash

python3 object_detection_camera.py --model ../test_data/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite --label ../test_data/coco_labels.txt
