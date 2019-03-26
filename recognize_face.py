from picamera import PiCamera
from espeak import espeak
import cv2 as cv
import argparse
import boto3
import time
import os

def recognizeFace(client,image,collection):
	face_matched = False
	with open(image, 'rb') as file:
		response = client.search_faces_by_image(CollectionId=collection, Image={'Bytes': file.read()}, MaxFaces=1, FaceMatchThreshold=85)
	        if (not response['FaceMatches']):
			face_matched = False
	        else:
			face_matched = True
	return face_matched, response

def detectFace(frame,face_cascade):	
	face_detected = False
	#Detect faces
	faces = face_cascade.detectMultiScale(frame,
		scaleFactor=1.1,
		minNeighbors=5,
		minSize=(30, 30),
		flags = cv.CASCADE_SCALE_IMAGE)
	print("Found {0} faces!".format(len(faces)))
	timestr = time.strftime("%Y%m%d-%H%M%S")
	image = '{0}/image_{1}.png'.format(directory, timestr)
	if len(faces) > 0 :
		face_detected = True
		cv.imwrite(image,frame) 
	return face_detected, image

def main():	

	#get args
	parser = argparse.ArgumentParser(description='Facial recognition')
	parser.add_argument('--collection', help='Collection Name', default='chappie-faces')
	parser.add_argument('--face_cascade', help='Path to face cascade.', default='../opencv/data/haarcascades/haarcascade_frontalface_alt2.xml')
	parser.add_argument('--camera', help='Camera device number.', type=int, default=0)
	args = parser.parse_args()

	#intialize opencv face detection
	face_cascade_name = args.face_cascade
	face_cascade = cv.CascadeClassifier()

	#Load the cascades
	if not face_cascade.load(cv.samples.findFile(face_cascade_name)):
		print('--(!)Error loading face cascade')
		exit(0)

	camera_device = args.camera

	#Read the video stream
	cam = cv.VideoCapture(camera_device)

	if not cam.isOpened:
		print('--(!)Error opening video capture')
		exit(0)

	#initialize reckognition sdk
	client = boto3.client('rekognition')

	while True:
		ret, frame = cam.read()
		if frame is None:
			print('--(!) No captured frame -- Break!')
			break
		face_detected, image = detectFace(frame,face_cascade)
		if (face_detected):
			face_matched, response = recognizeFace(client, image , args.collection)
			if (face_matched):
				print 'Identity matched %s with %r similarity and %r confidence...' % (response['FaceMatches'][0]['Face']['ExternalImageId'], round(response['FaceMatches'][0]['Similarity'], 1), round(response['FaceMatches'][0]['Face']['Confidence'], 2))
				espeak.synth('Hello %s! What is my purpose?' % (response['FaceMatches'][0]['Face']['ExternalImageId']))
				print 'Hello %s! What is my purpose?' % (response['FaceMatches'][0]['Face']['ExternalImageId'])
			else:
				print 'Unknown Human Detected!'
				espeak.synth('Unknown human detected. Who are you stranger?')
			while espeak.is_playing:
				pass
			time.sleep(300)
		if cv.waitKey(20) & 0xFF == ord('q'):
			break

	# When everything done, release the capture
	cam.release()
	cv.destroyAllWindows()

dirname = os.path.dirname(__file__)
directory = os.path.join(dirname, 'faces')
main()

