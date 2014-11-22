import sys, os
from PIL import Image

DIR = os.path.dirname(os.path.realpath(__file__))

sampleSize = (64,64)

def downsampled(im):
	sampleImage = Image.new(im.mode, sampleSize, 0)
	samplePixels = sampleImage.load()

	for x in xrange(sampleImage.size[0]):
		for y in xrange(sampleImage.size[1]):
			samplePixels[x,y] = im.getpixel((x*8,y*8))

	return sampleImage

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
				binaryPixels[x, y] = 0
			elif originalPixel >= binaryThreshold and originalPixel <= 255:
				binaryPixels[x, y] = 255

	return binaryImage

def getValue(image, x, y):
	if x >= image.size[0] or x < 0 or y >= image.size[1] or y < 0:
		return 0
	return image.getpixel((x,y))



# 3x3 neighbors
# x7|x2|x6
#	x3|x0|x1
# x8|x4|x5
def getNeighbors( image, x, y ):
	return [getValue(image, x, y), getValue(image, x+1, y), getValue(image, x, y-1),       \
					getValue(image, x-1,y), getValue(image, x,y+1), getValue(image, x+1, y+1),     \
					getValue(image, x+1,y-1), getValue(image, x-1,y-1), getValue(image, x-1 ,y+1)]

def hFunc( b, c, d, e ):
	if b == c and (d!=b or e!=b):
		return 'q'
	elif b == c and (d==b or e==b):
		return 'r'
	elif b != c:
		return 's'

def fFunc(a1,a2,a3,a4):
	neighbors = [a1,a2,a3,a4]
	if( neighbors.count('r') == len(neighbors) ): # all neighbors are equal to r
		return 5
	else:
		return neighbors.count('q')

def Yokoi( neighbors ):
	return fFunc( \
						hFunc(neighbors[0],neighbors[1],neighbors[6],neighbors[2]), \
						hFunc(neighbors[0],neighbors[2],neighbors[7],neighbors[3]), \
						hFunc(neighbors[0],neighbors[3],neighbors[8],neighbors[4]), \
						hFunc(neighbors[0],neighbors[4],neighbors[5],neighbors[1]), \
				 )

if len( sys.argv ) == 2:
	im = Image.open( os.path.realpath(sys.argv[1]) )

	sampledImage = binarizing(downsampled(im));
	imageW = sampledImage.size[0]
	imageH = sampledImage.size[1]

	result = [[' ' for x in range(sampleSize[0])] for y in range(sampleSize[1])]

	for x in xrange(imageW):
		for y in xrange(imageH):
			if sampledImage.getpixel((x,y)) != 0:
				result[y][x] = Yokoi( getNeighbors( sampledImage, x, y ) )

	sampledImage.save('%s/sampled.jpg' % DIR)
	file = open("Yokoi.txt", "w")
	for y in xrange(sampleSize[1]):
		for x in xrange(sampleSize[0]):
			file.write(str(result[y][x]))
		file.write('\n')


else:
	print "ERROR: Image path is wrong. Please enter right image as second argument."
