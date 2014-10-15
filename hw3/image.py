import sys, os, csv
from PIL import Image, ImageDraw
from collections import OrderedDict

DIR = os.path.dirname(os.path.realpath(__file__))


#histogram equalization function
def equalize( value, cdf, cdfMin, imageW, imageH ):
	return round( float( cdf[value] - cdfMin )/float( imageW * imageH - cdfMin ) * 255 )


if len( sys.argv ) == 2:
	im = Image.open( os.path.realpath(sys.argv[1]) )
	imageW = im.size[0]
	imageH = im.size[1]

	# histogram
	histogram = [0 for i in xrange(256)]
	equalizedHistogram = [0 for i in xrange(256)]

	for x in xrange(imageW):
		for y in xrange(imageH):
			originalPixel = im.getpixel((x,y))
			histogram[originalPixel]+=1

  # get accumulated histogram and filter zero
	accumulated = OrderedDict()
	cdfMin = None
	for i in xrange(256):
		if histogram[i] == 0:
			continue
		elif len( accumulated ) == 0:
			accumulated[i] = histogram[i]
		else:
			# Add last element and current one
			accumulated[i] = accumulated[ next(reversed(accumulated)) ] + histogram[i]

		if( cdfMin is None and accumulated[i] != 0 ):
			cdfMin = accumulated[i]

	#output
	equalizedImage = Image.new(im.mode, im.size, 0)
	equalizedPixels = equalizedImage.load()

	for x in xrange(imageW):
		for y in xrange(imageH):
			originalPixel = im.getpixel((x,y))
			equalizedPixels[x,y] =  equalize(originalPixel, accumulated, cdfMin, imageW, imageH )
			equalizedHistogram[equalizedPixels[x,y]]+=1

	equalizedImage.save("%s/equalization.jpg" % DIR)

	hisFile = open('%s/histogram.csv' % DIR, "w")
	w = csv.writer(hisFile)
	w.writerow(equalizedHistogram)
	hisFile.close()

else:
	print "ERROR: Image path is wrong. Please enter right image as second argument."