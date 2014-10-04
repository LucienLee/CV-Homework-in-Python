import sys, os, csv
from PIL import Image

DIR = os.path.dirname(os.path.realpath(__file__))

binaryThreshold = 128

if len( sys.argv ) == 2:
	im = Image.open( os.path.realpath(sys.argv[1]) )
	imageW = im.size[0]
	imageH = im.size[1]


	# binarizing the image
	binaryImage = Image.new(im.mode, im.size, 0)
	binaryPixels = binaryImage.load()
	
	for x in xrange(imageW):
		for y in xrange(imageH):
			originalPixel = im.getpixel((x,y))
			if originalPixel < binaryThreshold:
				binaryPixels[x, y] = 0
			elif originalPixel >= binaryThreshold and originalPixel <= 255:
				binaryPixels[x, y] = 255

	binaryImage.save("%s/binarize.jpg" % DIR)

	# histogram
	histogram = [0 for i in xrange(255)]

	for x in xrange(imageW):
		for y in xrange(imageH):
			originalPixel = im.getpixel((x,y))
			histogram[originalPixel]+=1

	hisFile = open('%s/histogram.csv' % DIR, "w")
	w = csv.writer(hisFile)
	w.writerow(histogram)
	hisFile.close()

	# connected components
	connectImage = Image.new('RGB', im.size, 0)

else:
	print "ERROR: Image path is wrong. Please enter right image as second argument."