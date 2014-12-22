import sys, os, math, random
from PIL import Image, ImageDraw

DIR = os.path.dirname(os.path.realpath(__file__))

BLACK = 0
WHITE = 255

def getValue(image, x, y):
	if x >= image.size[0] or x < 0 or y >= image.size[1] or y < 0:
		return BLACK
	return image.getpixel((x,y))

def getNeighbors(image, origin, sizes):
	x = origin[0]
	y = origin[1]
	half = sizes[0]/2
	neighbors = [[0 for i in range(sizes[0])] for j in range(sizes[1])]

	for row in xrange(-half,  half+1):
		for col in xrange(-half, half+1):
			neighbors[half+col][half+row] = getValue(image,x+col,y+row)
	return neighbors

def L2NormMagnitude(neighbors, masks, threshold):
	num = len(masks)
	sizeX = len(masks[0])
	sizeY = len(masks[0][0])
	magnitude = []

	for i in xrange(num):
		r = 0
		for row in xrange(sizeY):
			for col in xrange(sizeX):
				r += neighbors[col][row]*masks[i][col][row]
		magnitude.append(r**2)
	return (math.sqrt(sum(magnitude)) > threshold)


def MaxMagnitude(neighbors, masks, threshold):
	num = len(masks)
	sizeX = len(masks[0])
	sizeY = len(masks[0][0])
	magnitude = []

	for i in xrange(num):
		r = 0
		for row in xrange(sizeY):
			for col in xrange(sizeX):
				r += neighbors[col][row]*masks[i][col][row]
		magnitude.append(r)
	return (max(magnitude) > threshold)

def robertDetector(origin, image, threshold):
	masks = [[[-1, 0], [0, 1]], [[0, -1],[1, 0]]]
	neighbors = []
	x = origin[0]
	y = origin[1]
	neighbors.append([ getValue(image,x,y), getValue(image,x+1,y) ])
	neighbors.append([ getValue(image,x,y+1), getValue(image,x+1,y+1) ])
	return BLACK if L2NormMagnitude(neighbors, masks, threshold) is True else WHITE

def prewittDetector(origin, image, threshold):
	masks = [[[-1, -1, -1], [0, 0, 0], [1, 1, 1]], [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]]
	neighbors = getNeighbors( image, origin, [3, 3])
	return BLACK if L2NormMagnitude(neighbors, masks, threshold) is True else WHITE

def sobelDetector(origin, image, threshold):
	masks = [[[-1, -2, -1], [0, 0, 0], [1, 2, 1]], [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]]
	neighbors = getNeighbors(image, origin, [3, 3])
	return BLACK if L2NormMagnitude(neighbors, masks, threshold) is True else WHITE

def freichenDetector(origin, image, threshold):
	sqrt2 = math.sqrt(2)
	masks = [[[-1, -sqrt2, -1], [0, 0, 0], [1, sqrt2, 1]], [[-1, 0, 1], [-sqrt2, 0, sqrt2], [-1, 0, 1]]]
	neighbors = getNeighbors(image, origin, [3, 3])
	return BLACK if L2NormMagnitude(neighbors, masks, threshold) is True else WHITE

def kirschDetector(origin, image, threshold):
	masks = [[[-3, -3, 5], [-3, 0, 5], [-3, -3, 5]],
					[[-3, 5, 5], [-3, 0, 5], [-3, -3, -3]],
					[[5, 5, 5], [-3, 0, -3], [-3, -3, -3]],
					[[5, 5, -3], [5, 0, -3], [-3, -3, -3]],
					[[5, -3, -3], [5, 0, -3], [5, -3, -3]],
					[[-3, -3, -3], [5, 0, -3], [5, 5, -3]],
					[[-3, -3, -3], [-3, 0, -3], [5, 5, 5]],
					[[-3, -3, -3], [-3, 0, 5], [-3, 5, 5]]]
	neighbors = getNeighbors(image, origin, [3, 3])
	return BLACK if MaxMagnitude(neighbors, masks, threshold) is True else WHITE

def robinsonDetector(origin, image, threshold):
	masks = [[[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
					[[0, -1, -2], [1, 0, -1], [2, 1, 0]],
					[[1, 0, -1], [2, 0, -2], [1, 0, -1]],
					[[2, 1, 0], [1, 0, -1], [0, -1, -2]],
					[[1, 2, 1], [0, 0, 0], [-1, -2, -1]],
					[[0, 1, 2], [-1, 0, 1], [-2, -1, 0]],
					[[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
					[[-2, -1, 0], [-1, 0, 1], [0, 1, 2]]]
	neighbors = getNeighbors(image, origin, [3, 3])
	return BLACK if MaxMagnitude(neighbors, masks, threshold) is True else WHITE

def nevatiababuDetector(origin, image, threshold):
	masks = [[[100, 100, 0, -100, -100], [100, 100, 0, -100, -100], [100, 100, 0, -100, -100], [100, 100, 0, -100, -100], [100, 100, 0, -100, -100]],
	[[100, 100, 100, 32, -100], [100, 100, 92, -78, -100], [100, 100, 0, -100, -100], [100, 78, -92, -100, -100], [100, -32, -100, -100, -100]],		
	[[100, 100, 100, 100, 100], [100, 100, 100, 78, -32], [100, 92, 0, -92, -100], [32, -78, -100, -100, -100], [-100, -100, -100, -100, -100]],
	[[-100, -100, -100, -100, -100], [-100, -100, -100, -100, -100], [0, 0, 0, 0, 0], [100, 100, 100, 100, 100], [100, 100, 100, 100, 100]],
	[[-100, -100, -100, -100, -100], [32, -78, -100, -100, -100], [100, 92, 0, -92, -100], [100, 100, 100, 78, -32], [100, 100, 100, 100, 100]],
	[[100, -32, -100, -100, -100], [100, 78, -92, -100, -100], [100, 100, 0, -100, -100], [100, 100, 92, -78, -100], [100, 100, 100, 32, -100]],
	]
	neighbors = getNeighbors(image, origin, [5, 5])
	return BLACK if MaxMagnitude(neighbors, masks, threshold) is True else WHITE

if( len( sys.argv ) == 2 ):
	image = Image.open( os.path.realpath(sys.argv[1]) )
	imageW = image.size[0]
	imageH = image.size[1]

	robertImage = Image.new(image.mode, image.size, 0)
	robertPixels = robertImage.load()
	prewittImage = Image.new(image.mode, image.size, 0)
	prewittPixels = prewittImage.load()
	sobelImage = Image.new(image.mode, image.size, 0)
	sobelPixels = sobelImage.load()
	freichenImage = Image.new(image.mode, image.size, 0)
	freichenPixels = freichenImage.load()
	kirschImage = Image.new(image.mode, image.size, 0)
	kirschPixels = kirschImage.load()
	robinsonImage = Image.new(image.mode, image.size, 0)
	robinsonPixels = robinsonImage.load()
	nevatiababuImage = Image.new(image.mode, image.size, 0)
	nevatiababuPixels = nevatiababuImage.load()

	for row in xrange(imageH):
		for col in xrange(imageW):
			robertPixels[col, row] = robertDetector((col,row), image, 12)
			prewittPixels[col, row] = prewittDetector((col,row), image, 24)
			sobelPixels[col, row] = sobelDetector((col,row), image, 38)
			freichenPixels[col, row] = freichenDetector((col,row), image, 30)
			kirschPixels[col, row] = kirschDetector((col,row), image, 135)
			robinsonPixels[col, row] = robinsonDetector((col,row), image, 43)
			nevatiababuPixels[col, row] = nevatiababuDetector((col,row), image, 12500)

	robertImage.save("%s/%s.jpg" % (DIR, "robert_30"))
	prewittImage.save("%s/%s.jpg" % (DIR, "prewitt_24"))
	sobelImage.save("%s/%s.jpg" % (DIR, "sobel_38"))
	freichenImage.save("%s/%s.jpg" % (DIR, "freichen_30"))
	kirschImage.save("%s/%s.jpg" % (DIR, "kirsch_135"))
	robinsonImage.save("%s/%s.jpg" % (DIR, "robinson_43"))
	nevatiababuImage.save("%s/%s.jpg" % (DIR, "nevatiababu_12500"))

else:
	print "ERROR: Image path is wrong. Please enter right image as second argument."