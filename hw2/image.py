import sys, os, csv
from PIL import Image, ImageDraw

DIR = os.path.dirname(os.path.realpath(__file__))

binaryThreshold = 128
areaThreshold = 500

class UnionFind(object):
    """Union-Find is a data structure for keeping track
    of partitions of sets into disjoint subsets"""

    def __init__(self):
        """Set up leader and group dictionaries"""
        self.leader = {}  # maps member to group leader
        self.group = {}   # maps group leader to set of members

    def __sort(self, element):
    	"""sort union leader as smallest one"""
        newleader = min(self.group[self.leader[element]])
        curleader = self.leader[element]
        curgroup = self.group[curleader]
        self.group[newleader] = self.group.pop(curleader)
        for i in curgroup:
            self.leader[i] = newleader

    def makeSet(self, elements):
        """Insert elements as new group"""
        assert type(elements) is list

        group = set(elements)
        self.group[elements[0]] = group
        for i in group:
            self.leader[i] = elements[0]

    def find(self, element):
        """Return the group associated with an element"""
        return self.leader[element]

    def show(self):
        print self.leader
        print self.group

    def union(self, element1, element2):
        """Merge the groups containing two different elements"""
        leader1 = self.leader[element1]
        leader2 = self.leader[element2]

        # If both elements are in same group, do nothing
        if leader1 == leader2:
            return

        # Otherwise, merge the two groups
        group1 = self.group[leader1]
        group2 = self.group[leader2]

        # Swap names if group1 is smaller than group2
        if len(group1) < len(group2):
            element1, leader1, group1, \
                element2, leader2, group2 = \
                element2, leader2, group2, \
                element1, leader1, group1

        # Merge group1 with group2, delete group2 and update leaders
        group1 |= group2
        del self.group[leader2]
        for i in group2:
            self.leader[i] = leader1

        self.__sort(leader1)

    def getNumGroups(self):
        """Return the number of groups"""
        return len(self.group)

class Rect(object):
	"""Data Struct for bounding box"""
	def __init__(self, imageW, imageH):
		self.x1 = imageW
		self.x2 = 0
		self.y1 = imageH
		self.y2 = 0

	def updateX(self, x):
		if( x < self.x1 ):
			self.x1 = x
		elif( x > self.x2 ):
			self.x2 = x
	def updateY(self, y):
		if( y < self.y1 ):
			self.y1 = y
		elif( y > self.y2 ):
			self.y2 = y

	def getXY(self):
		return [self.x1 ,self.y1, self.x2 ,self.y2]

def drawCross(coordinate, image):
	"""Draw cross in center of bounding box"""
	x1 = coordinate[0]
	y1 = coordinate[1]
	x2 = coordinate[2]
	y2 = coordinate[3]
	midx = int((x1 + x2) / 2)
	midy = int((y1 + y2) / 2)
	for i in xrange(x1, x2 + 1):
		for j in xrange(y1, y2 + 1):
			if i < (midx + 11) and i >= (midx - 10):
				if j < (midy + 5) and j > (midy - 5):
					image[i, j] = (255, 0, 0)
				if i < (midx + 5) and i > (midx - 5):
					if j < (midy + 11) and j >= (midy - 10):
						image[i, j] = (255, 0, 0)

if len( sys.argv ) == 2:
	im = Image.open( os.path.realpath(sys.argv[1]) )
	imageW = im.size[0]
	imageH = im.size[1]

	connectImage = Image.new('RGB', im.size, 0)
	conectPixels = connectImage.load()

	# binarizing the image
	binaryImage = Image.new(im.mode, im.size, 0)
	binaryPixels = binaryImage.load()

	for x in xrange(imageW):
		for y in xrange(imageH):
			originalPixel = im.getpixel((x,y))
			if originalPixel < binaryThreshold:
				binaryPixels[x, y] = 0
				conectPixels[x, y] = (0,0,0)
			elif originalPixel >= binaryThreshold and originalPixel <= 255:
				binaryPixels[x, y] = 255
				conectPixels[x, y] = (255,255,255)

	binaryImage.save("%s/binarize.jpg" % DIR)

	# histogram
	histogram = [0 for i in xrange(256)]

	for x in xrange(imageW):
		for y in xrange(imageH):
			originalPixel = im.getpixel((x,y))
			histogram[originalPixel]+=1

	hisFile = open('%s/histogram.csv' % DIR, "w")
	w = csv.writer(hisFile)
	w.writerow(histogram)
	hisFile.close()

	# connected labeling
	NextLabel = 0
	labels = [[0 for y in xrange(imageH)] for x in xrange(imageW)]
	UF = UnionFind()
	finalLabel = []
	Rects = {}

	# first pass
	for y in xrange(imageH):
		for x in xrange(imageW):
			if binaryPixels[x, y] is not 0:
				neighbor = {}
				if x - 1 >= 0 and binaryPixels[x, y] == binaryPixels[x - 1, y]:
					neighbor[( x-1 , y )] = labels[x - 1][y]
				if y - 1 >= 0 and binaryPixels[x, y] == binaryPixels[x, y - 1]:
					neighbor[( x, y-1 )] = labels[x][y - 1]

				if len(neighbor) == 0:
					NextLabel += 1
					labels[x][y] = NextLabel
					UF.makeSet([NextLabel])
				else:
					labels[x][y] = min(neighbor.values())
					if( len(neighbor) == 2 ):
						UF.union( neighbor.values()[0],  neighbor.values()[1] )

	areaCounter = [0 for i in xrange(NextLabel+1)]

	# second pass
	for y in xrange(imageH):
		for x in xrange(imageW):
			if binaryPixels[x, y] is not 0:
				labels[x][y] = UF.find(labels[x][y])
				areaCounter[labels[x][y]]+=1
				#filter
				if areaCounter[labels[x][y]] >= areaThreshold and labels[x][y] not in Rects.keys():
					Rects[labels[x][y]] = Rect(imageW, imageH)

	#get bounding box
	for y in xrange(imageH):
		for x in xrange(imageW):
			if( labels[x][y] in Rects.keys() ):
				Rects[labels[x][y]].updateX(x)
				Rects[labels[x][y]].updateY(y)

	for label, rect in Rects.items():
		draw = ImageDraw.Draw(connectImage)
		draw.rectangle(rect.getXY(), outline="red")
		drawCross(rect.getXY(), conectPixels)

	del draw
	connectImage.show()
	binaryImage.save("%s/boundingbox.jpg" % DIR)

else:
	print "ERROR: Image path is wrong. Please enter right image as second argument."