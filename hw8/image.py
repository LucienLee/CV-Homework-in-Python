import sys, os, math, random
from PIL import Image, ImageDraw

DIR = os.path.dirname(os.path.realpath(__file__))

BLACK = 0
WHITE = 255

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
	print "in dila"
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
	print "in ero"
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

def closingThenOpening( image, kernal):
	return opening( closing(image, kernal), kernal )

def openingThenClosing( image, kernal):
	return closing( opening(image, kernal), kernal )

def gaussianNoice( image, amplitude ):
	gaussianImage = image.copy()
	imageW = image.size[0]
	imageH = image.size[1]
	imagePixel = gaussianImage.load()

	for col in xrange(imageW):
		for row in xrange(imageH):
			noiseValue = imagePixel[ col ,row ] + amplitude*random.gauss(0,1)
			if noiseValue > WHITE :
				noiseValue = WHITE

			imagePixel[ col ,row ] = noiseValue

	return gaussianImage

def saltAndPepper( image, threshold ):
	saltImage = image.copy()
	imageW = image.size[0]
	imageH = image.size[1]
	imagePixel = saltImage.load()

	for col in xrange(imageW):
		for row in xrange(imageH):
			randomValue = random.uniform(0,1)
			if randomValue < threshold :
				imagePixel[ col,row ] = BLACK
			elif randomValue > 1-threshold :
				imagePixel[ col,row ] = WHITE

	return saltImage

# Use all weight 1 as simple box
def boxFilter( image, boxWidth, boxHeight ):
	filteredImage = image.copy()
	imageW = image.size[0]
	imageH = image.size[1]
	imagePixel = filteredImage.load()

	for col in xrange(imageW):
		for row in xrange(imageH):
			boxList = []
			localOrigin = ( col-(boxWidth/2), row-(boxHeight/2) )
			for boxCol in xrange(boxWidth):
				for boxRow in xrange(boxHeight):
					x = localOrigin[0]+boxCol
					y = localOrigin[1]+boxRow
					if x>=0 and x<imageW and y>=0 and y<imageH:
						boxList.append( imagePixel[x,y] )

			imagePixel[col,row] = sum(boxList)/len(boxList)

	return filteredImage

def median(list):
    half = len(list) / 2
    list.sort()
    if len(list) % 2 == 0:
        return (list[half-1] + list[half])/ 2
    else:
        return list[half]

def medianFilter( image, boxWidth, boxHeight ):
	filteredImage = image.copy()
	imageW = image.size[0]
	imageH = image.size[1]
	imagePixel = filteredImage.load()

	for col in xrange(imageW):
		for row in xrange(imageH):
			boxList = []
			localOrigin = ( col-(boxWidth/2), row-(boxHeight/2) )
			for boxCol in xrange(boxWidth):
				for boxRow in xrange(boxHeight):
					x = localOrigin[0]+boxCol
					y = localOrigin[1]+boxRow
					if x>=0 and x<imageW and y>=0 and y<imageH:
						boxList.append( imagePixel[x,y] )

			imagePixel[col,row] = median(boxList)

	return filteredImage

def SNR( originImage, noiseImage ):
	imageW = originImage.size[0]
	imageH = originImage.size[1]
	size = imageW*imageH
	originPixel = originImage.load()
	noisePixel = noiseImage.load()
	us = 0
	vs = 0
	un = 0
	vn = 0

	for col in xrange(imageW):
		for row in xrange(imageH):
			us += originPixel[col, row]
	us /= size

	for col in xrange(imageW):
		for row in xrange(imageH):
			vs += math.pow( originPixel[col, row] - us, 2 )
	vs /= size

	for col in xrange(imageW):
		for row in xrange(imageH):
			un += noisePixel[col,row]-originPixel[col, row]
	un /= size

	for col in xrange(imageW):
		for row in xrange(imageH):
			vn += math.pow( noisePixel[col,row]-originPixel[col, row]-un, 2 )
	vn /= size

	return 20*math.log( math.sqrt(vs)/math.sqrt(vn), 10 )

if( len( sys.argv ) == 2 ):
	im = Image.open( os.path.realpath(sys.argv[1]) )
	octogonKernel = Kernel( (2,2), octogon )
	file = open("SNR.txt", "w")

	gaussian_10_Image = gaussianNoice( im, 10 )
	gaussian_30_Image = gaussianNoice( im, 30 )
	salt_005_Image = saltAndPepper( im, 0.05 )
	salt_01_Image = saltAndPepper( im, 0.1 )

	# gaussian_10_Image.save("%s/gaussian_10.jpg" % DIR)
	# gaussian_30_Image.save("%s/gaussian_30.jpg" % DIR)
	# salt_005_Image.save("%s/salt_005.jpg" % DIR)
	# salt_01_Image.save("%s/salt_01.jpg" % DIR)

	# box filter 3x3

	# box3x3_gaussian_10 = boxFilter( gaussian_10_Image, 3, 3)
	# box3x3_gaussian_30 = boxFilter( gaussian_30_Image, 3, 3)
	# box3x3_salt_005 = boxFilter( salt_005_Image, 3, 3)
	# box3x3_salt_01 = boxFilter( salt_01_Image, 3, 3)

	# box3x3_gaussian_10.save("%s/box3x3_gaussian_10.jpg" % DIR)
	# box3x3_gaussian_30.save("%s/box3x3_gaussian_30.jpg" % DIR)
	# box3x3_salt_005.save("%s/box3x3_salt_005.jpg" % DIR)
	# box3x3_salt_01.save("%s/box3x3_salt_01.jpg" % DIR)

	# file.write( "box3x3_gaussian_10: "+ str(SNR(im, box3x3_gaussian_10)) + '\n' )
	# file.write( "box3x3_gaussian_30: "+ str(SNR(im, box3x3_gaussian_30)) + '\n' )
	# file.write( "box3x3_salt_005: "+ str(SNR(im, box3x3_salt_005)) + '\n' )
	# file.write( "box3x3_salt_01: "+ str(SNR(im, box3x3_salt_01)) + '\n' )

	# box filter 5x5

	# box5x5_gaussian_10 = boxFilter( gaussian_10_Image, 5, 5)
	# box5x5_gaussian_30 = boxFilter( gaussian_30_Image, 5, 5)
	# box5x5_salt_005 = boxFilter( salt_005_Image, 5, 5)
	box5x5_salt_01 = boxFilter( salt_01_Image, 5, 5)

	# box5x5_gaussian_10.save("%s/box5x5_gaussian_10.jpg" % DIR)
	# box5x5_gaussian_30.save("%s/box5x5_gaussian_30.jpg" % DIR)
	# box5x5_salt_005.save("%s/box5x5_salt_005.jpg" % DIR)
	box5x5_salt_01.save("%s/box5x5_salt_01.jpg" % DIR)

	# file.write( "box5x5_gaussian_10: "+ str(SNR(im, box5x5_gaussian_10)) + '\n' )
	# file.write( "box5x5_gaussian_30: "+ str(SNR(im, box5x5_gaussian_30)) + '\n' )
	# file.write( "box5x5_salt_005: "+ str(SNR(im, box5x5_salt_005)) + '\n' )
	file.write( "box5x5_salt_01: "+ str(SNR(im, box5x5_salt_01)) + '\n' )

	# median filter 3x3

	# median3x3_gaussian_10 = medianFilter( gaussian_10_Image, 3, 3)
	# median3x3_gaussian_30 = medianFilter( gaussian_30_Image, 3, 3)
	# median3x3_salt_005 = medianFilter(salt_005_Image, 3, 3)
	median3x3_salt_01 = medianFilter(salt_01_Image, 3, 3)

	# median3x3_gaussian_10.save("%s/median3x3_gaussian_10.jpg" % DIR)
	# median3x3_gaussian_30.save("%s/median3x3_gaussian_30.jpg" % DIR)
	# median3x3_salt_005.save("%s/median3x3_salt_005.jpg" % DIR)
	median3x3_salt_01.save("%s/median3x3_salt_01.jpg" % DIR)

	# file.write( "median3x3_gaussian_10: "+ str(SNR(im, median3x3_gaussian_10)) + '\n' )
	# file.write( "median3x3_gaussian_30: "+ str(SNR(im, median3x3_gaussian_30)) + '\n' )
	# file.write( "median3x3_salt_005: "+ str(SNR(im, median3x3_salt_005)) + '\n' )
	# file.write( "median3x3_salt_01: "+ str(SNR(im, median3x3_salt_01)) + '\n' )

	# median filter 5x5

	# median5x5_gaussian_10 = medianFilter( gaussian_10_Image, 5, 5)
	# median5x5_gaussian_30 = medianFilter( gaussian_30_Image, 5, 5)
	# median5x5_salt_005 = medianFilter(salt_005_Image, 5, 5)
	median5x5_salt_01 = medianFilter(salt_01_Image, 5, 5)

	# median5x5_gaussian_10.save("%s/median5x5_gaussian_10.jpg" % DIR)
	# median5x5_gaussian_30.save("%s/median5x5_gaussian_30.jpg" % DIR)
	# median5x5_salt_005.save("%s/median5x5_salt_005.jpg" % DIR)
	median5x5_salt_01.save("%s/median5x5_salt_01.jpg" % DIR)

	# file.write( "median5x5_gaussian_10: "+ str(SNR(im, median5x5_gaussian_10)) + '\n' )
	# file.write( "median5x5_gaussian_30: "+ str(SNR(im, median5x5_gaussian_30)) + '\n' )
	# file.write( "median5x5_salt_005: "+ str(SNR(im, median5x5_salt_005)) + '\n' )
	file.write( "median5x5_salt_01: "+ str(SNR(im, median5x5_salt_01)) + '\n' )

	# closingThenOpening_gaussian_10 = closingThenOpening( gaussian_10_Image, octogonKernel)
	# closingThenOpening_gaussian_30 = closingThenOpening( gaussian_30_Image, octogonKernel)
	# closingThenOpening_salt_005 = closingThenOpening( salt_005_Image, octogonKernel)
	# closingThenOpening_salt_01 = closingThenOpening( salt_01_Image, octogonKernel)

	# closingThenOpening_gaussian_10.save("%s/closingThenOpening_gaussian_10.jpg" % DIR)
	# closingThenOpening_gaussian_30.save("%s/closingThenOpening_gaussian_30.jpg" % DIR)
	# closingThenOpening_salt_005.save("%s/closingThenOpening_salt_005.jpg" % DIR)
	# closingThenOpening_salt_01.save("%s/closingThenOpening_salt_01.jpg" % DIR)

	# file.write( "closingThenOpening_gaussian_10: "+ str(SNR(im, closingThenOpening_gaussian_10)) + '\n' )
	# file.write( "closingThenOpening_gaussian_30: "+ str(SNR(im, closingThenOpening_gaussian_30)) + '\n' )
	# file.write( "closingThenOpening_salt_005: "+ str(SNR(im, closingThenOpening_salt_005)) + '\n' )
	# file.write( "closingThenOpening_salt_01: "+ str(SNR(im, closingThenOpening_salt_01)) + '\n' )

	# openingThenClosing_gaussian_10 = openingThenClosing( gaussian_10_Image, octogonKernel)
	# openingThenClosing_gaussian_30 = openingThenClosing( gaussian_30_Image, octogonKernel)
	# openingThenClosing_salt_005 = openingThenClosing( salt_005_Image, octogonKernel)
	# openingThenClosing_salt_01 = openingThenClosing( salt_01_Image, octogonKernel)

	# openingThenClosing_gaussian_10.save("%s/openingThenClosing_gaussian_10.jpg" % DIR)
	# openingThenClosing_gaussian_30.save("%s/openingThenClosing_gaussian_30.jpg" % DIR)
	# openingThenClosing_salt_005.save("%s/openingThenClosing_salt_005.jpg" % DIR)
	# openingThenClosing_salt_01.save("%s/openingThenClosing_salt_01.jpg" % DIR)

	# file.write( "openingThenClosing_gaussian_10: "+ str(SNR(im, openingThenClosing_gaussian_10)) + '\n' )
	# file.write( "openingThenClosing_gaussian_30: "+ str(SNR(im, openingThenClosing_gaussian_30)) + '\n' )
	# file.write( "openingThenClosing_salt_005: "+ str(SNR(im, openingThenClosing_salt_005)) + '\n' )
	# file.write( "openingThenClosing_salt_01: "+ str(SNR(im, openingThenClosing_salt_01)) + '\n' )

	file.close()

else:
	print "ERROR: Image path is wrong. Please enter right image as second argument."