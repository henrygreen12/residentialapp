# USAGE
# python test_network.py --model santa_not_santa.model --image examples/santa_01.png
# python test_network.py --model furnace_not_furnace.model --image examples/santa_01.png
# import the necessary packages

import numpy as np
import argparse
import imutils
import cv2
import googleapiclient.discovery
from apiclient import discovery
from google.api_core.client_options import ClientOptions
import os

root_path = os.path.dirname(os.path.abspath(__file__))
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = root_path+"/My First Project-580d9a3220f1.json" #API



def predict_json(project, region, model, instances, version=None):
    """Send json data to a deployed model for prediction.

    Args:
        project (str): project where the Cloud ML Engine Model is deployed.
        region (str): regional endpoint to use; set to None for ml.googleapis.com
        model (str): model name.
        instances ([Mapping[str: Any]]): Keys should be the names of Tensors
            your deployed model expects as inputs. Values should be datatypes
            convertible to Tensors, or (potentially nested) lists of datatypes
            convertible to tensors.
        version: str, version of the model to target.
    Returns:
        Mapping[str: any]: dictionary of prediction results defined by the
            model.
    """
    # Create the ML Engine service object.
    # To authenticate set the environment variable
    # GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>
    prefix = "{}-ml".format(region) if region else "ml"
    api_endpoint = "https://{}.googleapis.com".format(prefix)
    client_options = ClientOptions(api_endpoint=api_endpoint)
    service = googleapiclient.discovery.build(
        'ml', 'v1', client_options=client_options)
    name = 'projects/{}/models/{}'.format(project, model)

    if version is not None:
        name += '/versions/{}'.format(version)

    response = service.projects().predict(
        name=name,
        body={'instances': instances}
    ).execute()

    print(response)

    if 'error' in response:
        raise RuntimeError(response['error'])

    return response['predictions']




def is_furnace(image_array):
    # pre-process the image for classification


    prediction = predict_json('trusty-moment-288519','us-central1', 'furnace_not_furnace', image_array)


    # classify the input image
    (not_furnace, furnace) = prediction[0]
    print(furnace)

    # build the label
    label = "Furnace" if furnace > not_furnace else "Not Furnace"
    proba = furnace if furnace > not_furnace else not_furnace

    return [label,proba]
