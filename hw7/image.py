# Zhang-Suen Thinning Algorithm
import sys, os
from PIL import Image

DIR = os.path.dirname(os.path.realpath(__file__))

WHITE = 255
BLACK = 0

def binarizing(image):
	imageW = image.size[0]
	imageH = image.size[1]
	binaryThreshold = 128
	binaryImage = Image.new(image.mode, image.size, 0)
	binaryPixels = binaryImage.load()

	for x in xrange(imageW):
		for y in xrange(imageH):
			originalPixel = image.getpixel((x,y))
			if originalPixel < binaryThreshold:
				binaryPixels[x, y] = BLACK
			elif originalPixel >= binaryThreshold and originalPixel <= WHITE:
				binaryPixels[x, y] = WHITE

	return binaryImage

def getValue(image, x, y):
	if x >= image.size[0] or x < 0 or y >= image.size[1] or y < 0:
		return BLACK
	return image.getpixel((x,y))/WHITE

# 3x3 neighbors
# x8|x1|x2
#	x7|x0|x3
# x6|x5|x4
def getNeighbors( image, x, y ):
	return [getValue(image, x, y), getValue(image, x, y-1), getValue(image, x+1, y-1),       \
					getValue(image, x+1,y), getValue(image, x+1,y+1), getValue(image, x, y+1),       \
					getValue(image, x-1,y+1), getValue(image, x-1,y), getValue(image, x-1 ,y-1)]


def clockwiseCheck(neighbors):
	counter = 0
	local = list(neighbors)
	del local[0]
	local.append(local[0])

	for i in xrange(0, len(local)):
		if i+1 < len(local):
			if local[i] < local[i+1] :
				counter+=1

	if counter == 1:
		return True
	else:
		return False


# delete pixel when retrun true
def firstThinning( neighbors ):
	if sum(neighbors)-neighbors[0] >= 2 and sum(neighbors)-neighbors[0] <=6 and clockwiseCheck(neighbors):
		if( neighbors[1]*neighbors[3]*neighbors[5] == 0 and neighbors[3]*neighbors[5]*neighbors[7] == 0 ):
			return True
	return False

# delete pixel when retrun true
def secondThinning( neighbors ):
	if sum(neighbors)-neighbors[0] >= 2 and sum(neighbors)-neighbors[0] <=6 and clockwiseCheck(neighbors):
		if( neighbors[1]*neighbors[3]*neighbors[7] == 0 and neighbors[1]*neighbors[5]*neighbors[7] == 0 ):
			return True
	return False

if len( sys.argv ) == 2:
	image = Image.open( os.path.realpath(sys.argv[1]) )

	binaryImage = binarizing(image);
	binaryPixels = binaryImage.load()
	imageW = binaryImage.size[0]
	imageH = binaryImage.size[1]

	thinningImage = Image.new(image.mode, image.size, 0)
	thinningPixels = thinningImage.load()

	counter = 0
	#thinning
	while True:
		notChange = True
		delete = []
		for x in xrange(imageW):
			for y in xrange(imageH):
				if binaryPixels[x, y]:
					if firstThinning( getNeighbors(binaryImage, x, y) ) :
						delete.append( (x,y) )
						notChange = False

		for pixel in delete:
			binaryPixels[pixel[0], pixel[1]] = BLACK
			del pixel

		for x in xrange(imageW):
			for y in xrange(imageH):
				if binaryPixels[x, y]:
					if secondThinning( getNeighbors(binaryImage, x, y) ) :
						delete.append( (x,y) )
						notChange = False

		for pixel in delete:
			binaryPixels[pixel[0], pixel[1]] = BLACK
			del pixel

		if( notChange ):
			break

	binaryImage.show()

else:
	print "ERROR: Image path is wrong. Please enter right image as second argument."
