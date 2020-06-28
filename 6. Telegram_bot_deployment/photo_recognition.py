from imageai.Detection import ObjectDetection

import numpy as np
import pandas as pd

import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

# from collections import defaultdict
from io import StringIO
from PIL import Image
# from IPython.display import display

import pathlib

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# Should asks user to upload file (or in regression?)
# Analyses uploaded photo
# Returns list with words (what on photo)


# Photo object detection
def load_model(model_name):
    """
    Loads model from the Internet
    :param model_name
    :return: model
    """
    base_url = 'http://download.tensorflow.org/models/object_detection/'
    model_file = model_name + '.tar.gz'
    model_dir = tf.keras.utils.get_file(
        fname=model_name,
        origin=base_url + model_file,
        untar=True)

    model_dir = pathlib.Path(model_dir) / "saved_model"

    model = tf.saved_model.load(str(model_dir))
    model = model.signatures['serving_default']

    return model


# Loading object labels
PATH_TO_LABELS = 'models/research/object_detection/data/mscoco_label_map.pbtxt'
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
# Used model name to upload model
model_name = 'faster_rcnn_resnet101_coco_11_06_2017'
detection_model = load_model(model_name)


def run_inference_for_single_image(model, image):
    """
    Predicts what is on photo
    :param model
    :param image
    :return: dictionary with information what is on photo
    """
    image = np.asarray(image)
    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis,...]

  # Run inference
    output_dict = model(input_tensor)

  # All outputs are batches tensors.
  # Convert to numpy arrays, and take index [0] to remove the batch dimension.
  # We're only interested in the first num_detections.
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key:value[0, :num_detections].numpy()
                 for key,value in output_dict.items()}
    output_dict['num_detections'] = num_detections

    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

    return output_dict


def show_inference(model, image_path):
    """
    Forms output as a list of predicted labels with probability > 0.5
    :param model:
    :param image_path:
    :return: list of predicted labels and probability
    """
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    image_np = np.array(Image.open(image_path))
    # Actual detection.
    output_dict = run_inference_for_single_image(model, image_np)

    labels_scores = []
    for i in range(len(output_dict['detection_classes'])):
        if output_dict['detection_scores'][i] > 0.5:
            labels_scores.append(category_index[output_dict['detection_classes'][i]]['name'])
    return labels_scores

# execution of object detection
def what_on_photo(path):
    """
    Used functions above to recognize what on photo
    :return: list of words
    """
    PATH_TO_IMAGES_DIR = pathlib.Path(path)
    IMAGE_PATHS = sorted(list(PATH_TO_IMAGES_DIR.glob("*.jpg")))
    what_on_photo = []
    for image_path in IMAGE_PATHS:
        labels = show_inference(detection_model, image_path)
        what_on_photo.extend(labels)

    return what_on_photo
