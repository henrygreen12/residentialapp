import csv
import boto3
import os


root_path = os.path.dirname(os.path.abspath(__file__))


with open(root_path+'/credentials.csv', 'r') as input:
    next(input)
    reader = csv.reader(input)
    for line in reader:
        access_key_id = line[2]
        secret_access_key = line[3]



def aws_rek(photo):





    client = boto3.client('rekognition', region_name='ap-southeast-1', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

    with open(photo,'rb') as source_image:
        source_bytes= source_image.read()



    response = client.detect_labels(Image={'Bytes':source_bytes},MaxLabels=10,MinConfidence=55)

    print(response)

    items = dict()
    items_list = []


    print('Detected labels for ' + photo)
    print()
    for label in response['Labels']:
        print ("Label: " + label['Name'])
        print ("Confidence: " + str(label['Confidence']))
        print ("Instances:")
        items[label['Name'].lower()] = label['Confidence']
        items_list.append(label['Name'])
        for instance in label['Instances']:
            print ("  Bounding box")
            print ("    Top: " + str(instance['BoundingBox']['Top']))
            print ("    Left: " + str(instance['BoundingBox']['Left']))
            print ("    Width: " +  str(instance['BoundingBox']['Width']))
            print ("    Height: " +  str(instance['BoundingBox']['Height']))
            print ("  Confidence: " + str(instance['Confidence']))
            print()

        print ("Parents:")
        for parent in label['Parents']:
            print ("   " + parent['Name'])
        print ("----------")
        print ()
    return items_list,items
