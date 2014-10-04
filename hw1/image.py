import sys, os
from PIL import Image

DIR = os.path.dirname(os.path.realpath(__file__))

if len( sys.argv ) == 2:
	im = Image.open( os.path.realpath(sys.argv[1]) )
	imageW = im.size[0]
	imageH = im.size[1]

	upsideDownImage = Image.new(im.mode, im.size, 0)
	upsideDownPixel = upsideDownImage.load()
	rightsideLeftImage = Image.new(im.mode, im.size, 0)
	rightsideLeftPixel = rightsideLeftImage.load()
	diagonallyImage = Image.new(im.mode, im.size, 0)
	diagonallyPixel = diagonallyImage.load()

	for x in range(0, imageW):
		for y in range(0, imageH):
			 originalPixel = im.getpixel((x,y))
			 rightsideLeftPixel[ imageW-1 - x, y ] = originalPixel
			 upsideDownPixel[ x, imageH-1 - y ] = originalPixel
			 diagonallyPixel[ y, x ] = originalPixel

	upsideDownImage.save("%s/upsideDownImage.BMP" % DIR)
	rightsideLeftImage.save("%s/rightsideLeftImage.BMP" % DIR)
	diagonallyImage.save("%s/diagonallyImage.BMP" % DIR)

else:
	print "ERROR: Image path is wrong. Please enter right image as second argument."
