#AIzaSyCElSBbyXGyGccibEifrgvjvWrRw_5Ut1I

import operator
import os
import sys

root_path = os.path.dirname(os.path.abspath(__file__))

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = root_path+"/MyFirstProject-aa47e5bcc8a2.json" #API



def localize_objects(path):
    """Localize objects in the local image.

    Args:
    path: The path to the local file.
    """
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)

    objects = client.object_localization(
        image=image).localized_object_annotations
    items = dict()
    for object_ in objects:
        items[str(object_.name)] = (object_.score)
        return items



import argparse
import io

from google.cloud import vision
from google.cloud.vision import types


def annotate(path):
    """Returns web annotations given the path to an image."""
    client = vision.ImageAnnotatorClient()

    if path.startswith('http') or path.startswith('gs:'):
        image = types.Image()
        image.source.image_uri = path

    else:
        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = types.Image(content=content)

    web_detection = client.web_detection(image=image).web_detection

    return web_detection


def report(annotations):
    """Prints detected features in the provided web annotations."""

    items = dict()

    for entity in annotations.web_entities:

        items[str(format(entity.description))] = format(entity.score)

    return(items)

def image_reck_appliance(image):
    x = localize_objects(image)
    y = max(x.items(), key=operator.itemgetter(1))[0]
    return y.lower()


