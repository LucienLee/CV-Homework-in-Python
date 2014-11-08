import sys, os
from PIL import Image, ImageDraw

DIR = os.path.dirname(os.path.realpath(__file__))

# n = no value, others are kernal value which range is 0~255
octogon = [
	['n', 0 , 0 , 0 ,'n'],
	[ 0 , 0 , 0 , 0 , 0 ],
	[ 0 , 0 , 0 , 0 , 0 ],
	[ 0 , 0 , 0 , 0 , 0 ],
	['n', 0 , 0 , 0 ,'n']
]

class Kernel(object):
	def __init__(self, origin, pattern):
		points = [] #store all points relative to origin
		for y in xrange( len(pattern) ):
			for x in xrange( len(pattern[ 0 ]) ):
				# reverse matrix x and y
				if(pattern[y][x] != 'n'):
					points.append(( x-origin[0],y-origin[1], pattern[y][x] ))
		self.points = points

	def getPoints(self):
		# get all points in (x,y,value)
		return self.points

def dilation( image, kernel ):
	imageW = image.size[0]
	imageH = image.size[1]
	dilationImage = Image.new(image.mode, image.size, 0)
	dilationPixels = dilationImage.load()

	for x in xrange(imageW):
		for y in xrange(imageH):
			originalPixel = image.getpixel((x,y))
			localMax = 0
			for point in kernel.getPoints():
				# edge detect
				if( x+point[0]>=0 and x+point[0]<imageW and y+point[1]>=0 and y+point[1]<imageH ):
					localMax = max( localMax, image.getpixel((x+point[0],y+point[1])) )
			dilationPixels[ x, y ] = localMax

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
			localMin = 255
			for point in kernel.getPoints():
				if( x+point[0]>=0 and x+point[0]<imageW and y+point[1]>=0 and y+point[1]<imageH ):
					if image.getpixel((x+point[0],y+point[1]) ) == 0 :
						vaildate = False
						break
					else:
						localMin = min( localMin, image.getpixel((x+point[0],y+point[1])) )
				else:
					vaildate = False
					break
			if vaildate :
				erosionPixels[x, y] = localMin

	return erosionImage

def opening( image, kernel ):
	return dilation( erosion(image, kernel), kernel )

def closing( image, kernel ):
	return erosion( dilation(image, kernel), kernel )

if( len( sys.argv ) == 2 ):
	im = Image.open( os.path.realpath(sys.argv[1]) )
	octogonKernel = Kernel( (2,2), octogon )

	dilaImage = dilation(im, octogonKernel)
	dilaImage.save("%s/dilation.jpg" % DIR)

	erosImage = erosion(im, octogonKernel)
	erosImage.save("%s/erosion.jpg" % DIR)

	openImage = opening(im, octogonKernel)
	openImage.save("%s/opening.jpg" % DIR)

	closeImage = closing(im, octogonKernel)
	closeImage.save("%s/closing.jpg" % DIR)


else:
	print "ERROR: Image path is wrong. Please enter right image as second argument."