# USAGE
# python3 test_network.py --model pvc_steel.model --image examples/santa_01.png
#

# import the necessary packages


import numpy as np
import imutils
import cv2
import googleapiclient.discovery
from apiclient import discovery
from google.api_core.client_options import ClientOptions
from .furnace_detect import *
import os

root_path = os.path.dirname(os.path.abspath(__file__))
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = root_path+"/My First Project-580d9a3220f1.json" #API


def is_pvc(image_array):

    prediction = predict_json('trusty-moment-288519','us-central1', 'pvc_steel', image_array)

    # classify the input image
    (steel, pvc) = prediction[0]
    # build the label
    label = "PVC" if pvc > steel else "Steel"
    proba = pvc if pvc > steel else steel
    return [label,proba]
