import sys, os
from PIL import Image, ImageDraw

DIR = os.path.dirname(os.path.realpath(__file__))

octogon = [
	[0,1,1,1,0],
	[1,1,1,1,1],
	[1,1,1,1,1],
	[1,1,1,1,1],
	[0,1,1,1,0]
]

Lpattern = [
	[1,1],
	[0,1]
]

class Kernel(object):
	def __init__(self, origin, pattern):
		points = [] #store all points relative to origin
		for y in xrange( len(pattern) ):
			for x in xrange( len(pattern[0]) ):
				# reverse matrix x and y
				if(pattern[y][x] == 1):
					points.append((x-origin[0],y-origin[1]))
		self.points = points

	def getPoints(self):
		return self.points

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


def reverse( image ):
	imageW = image.size[0]
	imageH = image.size[1]

	reverseImage = Image.new(image.mode, image.size, 0)
	reversePixels = reverseImage.load()

	for x in xrange(imageW):
		for y in xrange(imageH):
			originalPixel = image.getpixel((x,y))
			if( originalPixel == 255 ):
				reversePixels[x, y] = 0
			else:
				reversePixels[x, y] = 255

	return reverseImage

def intersect( image1, image2 ):
	imageW = image1.size[0]
	imageH = image1.size[1]

	intersectImage = Image.new(image1.mode, image1.size, 0)
	intersectPixels = intersectImage.load()

	for x in xrange(imageW):
		for y in xrange(imageH):
			image1Pixel = image1.getpixel((x,y))
			image2Pixel = image2.getpixel((x,y))
			if( image1Pixel == 255 and image2Pixel == 255 ):
				intersectPixels[x ,y] = 255
			else:
				intersectPixels[x ,y] = 0

	return intersectImage

def OR( image1, image2 ):
	imageW = image1.size[0]
	imageH = image1.size[1]

	orImage = Image.new(image1.mode, image1.size, 0)
	orPixels = orImage.load()

	for x in xrange(imageW):
		for y in xrange(imageH):
			image1Pixel = image1.getpixel((x,y))
			image2Pixel = image2.getpixel((x,y))
			if( image1Pixel == 255 or image2Pixel == 255 ):
				orPixels[x ,y] = 255
			else:
				orPixels[x ,y] = 0

	return orImage

def dilation( image, kernel ):
	imageW = image.size[0]
	imageH = image.size[1]
	dilationImage = Image.new(image.mode, image.size, 0)
	dilationPixels = dilationImage.load()

	for x in xrange(imageW):
		for y in xrange(imageH):
			originalPixel = image.getpixel((x,y))
			if( originalPixel == 255 ):
				for point in kernel.getPoints():
					# edge detect
					if( x+point[0]>=0 and x+point[0]<imageW and y+point[1]>=0 and y+point[1]<imageH ):
						dilationPixels[ x+point[0], y+point[1] ] = 255

	return dilationImage

def erosion( image, kernel ):
	imageW = image.size[0]
	imageH = image.size[1]
	erosionImage = Image.new(image.mode, image.size, 0)
	erosionPixels = erosionImage.load()

	for x in xrange(imageW):
		for y in xrange(imageH):
			originalPixel = image.getpixel((x,y))
			vaildate = True
			for point in kernel.getPoints():
				if( x+point[0]>=0 and x+point[0]<imageW and y+point[1]>=0 and y+point[1]<imageH ):
					if( image.getpixel((x+point[0],y+point[1]) ) != 255 ):
						vaildate = False
						break
				else:
					vaildate = False
					break
			if( vaildate ):
				erosionPixels[x, y] = 255

	return erosionImage

def opening( image, kernel ):
	return dilation( erosion(image, kernel), kernel )

def closing( image, kernel ):
	return erosion( dilation(image, kernel), kernel )

def hitAndMiss( image, jKernel, kKernel ):
	return intersect( erosion(image, jKernel), erosion( reverse(image), kKernel ) )

if( len( sys.argv ) == 2 ):
	im = Image.open( os.path.realpath(sys.argv[1]) )
	binaryIM = binarizing(im)
	octogonKernel = Kernel( (2,2), octogon )
	jKernel = Kernel( (1,0), Lpattern )
	kKernel = Kernel( (0,1), Lpattern )

	dilaImage = dilation(binaryIM, octogonKernel)
	dilaImage.save("%s/dilation.jpg" % DIR)

	erosImage = erosion(binaryIM, octogonKernel)
	erosImage.save("%s/erosion.jpg" % DIR)

	openImage = opening(binaryIM, octogonKernel)
	openImage.save("%s/opening.jpg" % DIR)

	closeImage = closing(binaryIM, octogonKernel)
	closeImage.save("%s/closing.jpg" % DIR)

	hitImage = hitAndMiss(binaryIM, jKernel, kKernel)
	hitImage.save("%s/hit and miss.jpg" % DIR)

else:
	print "ERROR: Image path is wrong. Please enter right image as second argument."