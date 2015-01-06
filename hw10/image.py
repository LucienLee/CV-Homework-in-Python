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


def calculateKernel(neighbors, mask, sizes, threshold, alpha):
	result = 0
	for y in xrange(sizes[1]):
		for x in xrange(sizes[0]):
			result += (neighbors[x][y] * mask[x][y])
	result *= alpha
	if result > threshold:
		return 1
	elif result < -threshold:
		return -1
	else:
		return 0

def checkNeighbors(position, labels, sizes):
	x = position[0]
	y = position[1]
	rawSize = len(labels)
	half = sizes[0]/2

	if labels[x][y] == 1:
		for row in xrange(-half,  half+1):
			for col in xrange(-half, half+1):
				if x+col >= 0 and x+col <= rawSize-1 and y+row >= 0 and y+row <=rawSize-1:
					# print x+col, y+row
					if labels[x+col][y+row] == -1:
						return 0

	return WHITE 


if( len( sys.argv ) == 2 ):
	image = Image.open( os.path.realpath(sys.argv[1]) )
	imageW = image.size[0]
	imageH = image.size[1]

	mask1 = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
	mask2 = [[1, 1, 1], [1, -8, 1], [1, 1, 1]]
	min_mask = [[2, -1, 2], [-1, -4, -1], [2, -1, 2]]
	gaussian_mask = [
		[0, 0, 0, -1, -1, -2, -1, -1, 0, 0, 0],
		[0, 0, -2, -4, -8, -9, -8, -4, -2, 0, 0],
		[0, -2, -7, -15, -22, -23, -22, -15, -7, -2, 0],
		[-1, -4, -15, -24, -14, -1, -14, -24, -15, -4, -1],
		[-1, -8, -22, -14, 52, 103, 52, -14, -22, -8, -1],
		[-2, -9, -23, -1, 103, 178, 103, -1, -23, -9, -2],
		[-1, -8, -22, -14, 52, 103, 52, -14, -22, -8, -1],
		[-1, -4, -15, -24, -14, -1, -14, -24, -15, -4, -1],
		[0, -2, -7, -15, -22, -23, -22, -15, -7, -2, 0],
		[0, 0, -2, -4, -8, -9, -8, -4, -2, 0, 0],
		[0, 0, 0, -1, -1, -2, -1, -1, 0, 0, 0]
	]
	dog_mask = [
		[-1, -3, -4, -6, -7, -8, -7, -6, -4, -3, -1],
		[-3, -5, -8, -11, -13, -13, -13, -11, -8, -5, -3],
		[-4, -8, -12, -16, -17, -17, -17, -16, -12, -8, -4],
		[-6, -11, -16, -16, 0, 15, 0, -16, -16, -11, -6],
		[-7, -13, -17, 0, 85, 160, 85, 0, -17, -13, -7],
		[-8, -13, -17, 15, 160, 283, 160, 15, -17, -13, -8],
		[-7, -13, -17, 0, 85, 160, 85, 0, -17, -13, -7],
		[-6, -11, -16, -16, 0, 15, 0, -16, -16, -11, -6],
		[-4, -8, -12, -16, -17, -17, -17, -16, -12, -8, -4],
		[-3, -5, -8, -11, -13, -13, -13, -11, -8, -5, -3],
		[-1, -3, -4, -6, -7, -8, -7, -6, -4, -3, -1]
	]

	laplacian1Image = Image.new(image.mode, image.size, 0)
	laplacian1Pixels = laplacian1Image.load()
	laplacian1Temp = [[0 for i in range(imageW)] for j in range(imageH)]
	laplacian2Image = Image.new(image.mode, image.size, 0)
	laplacian2Pixels = laplacian2Image.load()
	laplacian2Temp = [[0 for i in range(imageW)] for j in range(imageH)]
	minimumImage = Image.new(image.mode, image.size, 0)
	minimumPixels = minimumImage.load()
	minimumTemp = [[0 for i in range(imageW)] for j in range(imageH)]
	LOGImage = Image.new(image.mode, image.size, 0)
	LOGPixels = LOGImage.load()
	LOGTemp = [[0 for i in range(imageW)] for j in range(imageH)]
	DOGImage = Image.new(image.mode, image.size, 0)
	DOGPixels = DOGImage.load()
	DOGTemp = [[0 for i in range(imageW)] for j in range(imageH)]


	for row in xrange(imageH):
		for col in xrange(imageW):
			# laplacian1Temp[col][row] = calculateKernel(getNeighbors(image, (col,row), [3, 3]), mask1, [3, 3], 15, 1)
			# laplacian2Temp[col][row] = calculateKernel(getNeighbors(image, (col,row), [3, 3]), mask2, [3, 3], 15, 1/3.0)
			# minimumTemp[col][row] = calculateKernel(getNeighbors(image, (col,row),[3, 3]), min_mask, [3, 3], 20, 1/3.0)
			LOGTemp[col][row] = calculateKernel(getNeighbors(image, (col,row), [11,11]), gaussian_mask, [11, 11], 3000, 1)
			DOGTemp[col][row] = calculateKernel(getNeighbors(image, (col,row), [11,11]), dog_mask, [11, 11], 1, 1)
			
	for row in xrange(imageH):
		for col in xrange(imageW):
			# laplacian1Pixels[col, row] = checkNeighbors((col,row), laplacian1Temp, [3, 3])
			# laplacian2Pixels[col, row] = checkNeighbors((col,row), laplacian2Temp, [3, 3])
			# minimumPixels[col, row] = checkNeighbors((col,row), minimumTemp, [3, 3])
			LOGPixels[col, row] = checkNeighbors((col,row), LOGTemp, [11, 11])
			DOGPixels[col, row] = checkNeighbors((col,row), DOGTemp, [11, 11])
	
	# laplacian1Image.save("%s/%s.jpg" % (DIR, "laplacian1"))
	# laplacian2Image.save("%s/%s.jpg" % (DIR, "laplacian2"))
	# minimumImage.save("%s/%s.jpg" % (DIR, "minimum"))
	LOGImage.save("%s/%s.jpg" % (DIR, "LOG"))
	DOGImage.save("%s/%s.jpg" % (DIR, "DOG"))

else:
	print "ERROR: Image path is wrong. Please enter right image as second argument."