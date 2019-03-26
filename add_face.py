from picamera import PiCamera
import argparse
import boto3
import time
import os

#get args
parser = argparse.ArgumentParser(description='Capture image and add to collection.')
parser.add_argument('--collection', help='Collection Name', default='chappie-faces')
parser.add_argument('--name', help='Face Name')
args = parser.parse_args()

#capture photo using pi camera
camera = PiCamera()
dirname = os.path.dirname(__file__)
directory = os.path.join(dirname, 'faces')
timestr = time.strftime("%Y%m%d-%H%M%S")
image = '{0}/image_{1}.jpg'.format(directory, timestr)
time.sleep(0.5)
camera.capture(image)
print 'Your image was saved to %s' % image

#initialize reckognition sdk
client = boto3.client('rekognition')
with open(image, mode='rb') as file:
	response = client.index_faces(Image={'Bytes': file.read()}, CollectionId=args.collection, ExternalImageId=args.name, DetectionAttributes=['ALL'])
print response
