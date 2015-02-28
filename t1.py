#-*-coding:utf8-*-
import sys
from copy import deepcopy
import math

class RectSize(object):
    def __init__(self):
        self.width = 0
        self.height = 0

class Rect(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 0;
        self.height = 0;
        self.rotation_flag = False

    def init(self, rect, width, height, rotation=False):
        self.rotation_flag = rotation
        self.x = rect.x
        self.y = rect.y
        self.width = width
        self.height = height

class PackBin(object):
    def __init__(self):
        pass

    def init(self, width, height):
        self.binWidth = width
        self.binHeight = height
        self.functionDict = {'bottomleft': self.find_position_bottomleft,
                             'shortsidefit': self.find_position_bestshortsidefit,
                             'longsidefit': self.find_position_bestlongsidefit,
                             'areafit': self.find_position_bestareafit,
                             'contactpoint': self.find_position_contactpoint}
        n = Rect()
        n.x = 0
        n.y = 0
        n.width = width
        n.height = height

        self.usedRectList = []
        self.freeRectList = []
        self.freeRectList.append(n)

    def print_free_rect(self):
        for rect in self.freeRectList:
            print rect.__dict__

    def insert_online(self, width, height, fun_name):
        packFunction = self.functionDict[fun_name]
        newNode, _, _ = packFunction(width, height)
        if newNode.height == 0:
            raise Exception("Error pack online" + fun_name)
        #function split_free_rect will change the length of freeRectlist but the order
        del_index_list = []
        tmp_list = self.freeRectList[:]
        for i, freeNode in enumerate(tmp_list):
            if self.split_free_rect(freeNode, newNode):
                del_index_list.append(i)
        tmp_list = self.freeRectList
        self.freeRectList = []
        for i, node in enumerate(tmp_list):
            if i in del_index_list:
                continue
            self.freeRectList.append(node)
        self.prune_free_rect_list()
        self.usedRectList.append(newNode)
        return newNode

    def insert_offline(self, image_dict, fun_name):
        '''

        '''
        packFunction = self.functionDict[fun_name]
        names_list = image_dict.keys()
        remain_count = len(names_list)
        while remain_count > 0:
            bestScore1 = sys.maxint
            bestScore2 = sys.maxint
            bestRectIndex = -1
            bestNode = None
            for i, name in enumerate(names_list):
                newNode, score1, score2 = self.score_rect(
                    image_dict[name].width, image_dict[name].height, packFunction)
                if score1 < bestScore1 or (score1 == bestScore1 and score2 < bestScore2):
                    bestScore1 = score1
                    bestScore2 = score2
                    bestNode = newNode
                    bestRectIndex = i
            if bestRectIndex == -1:
                return
            self.place_rect(bestNode)
            #print '%s width: %d, height: %d  (%d, %d)'%(fun_name, bestNode.width, bestNode.height, bestNode.x, bestNode.y)
            image_dict[names_list[bestRectIndex]].node = bestNode
            del names_list[bestRectIndex]
            remain_count -= 1

    def place_rect(self, node):
        l = len(self.freeRectList)
        del_index_list= []
        for i, freeNode in enumerate(self.freeRectList[:l]):
            if self.split_free_rect(freeNode, node):
                del_index_list.append(i)
        tmp_list = self.freeRectList
        self.freeRectList = []
        for i in range(len(tmp_list)):
            if i in del_index_list:
                continue
            self.freeRectList.append(tmp_list[i])
        self.prune_free_rect_list()
        self.usedRectList.append(node)

    def score_rect(self, width, height, packFunction):
        score1 = score2 = sys.maxint
        newNode, score1, score2 = packFunction(width, height)
        if newNode.height == 0:
            raise Exception("Error pack offline" + str(packFunction))
        return newNode, score1, score2

    def find_position_bottomleft(self, width, height):
        bestNode = Rect()
        bestY = bestX = sys.maxint
        for i, freeNode in enumerate(self.freeRectList):
            if freeNode.width >= width and freeNode.height >= height:
                topSideY = freeNode.y + height
                if topSideY < bestY or (topSideY==bestY and freeNode.x<bestX):
                    bestNode.init(freeNode, width, height)
                    bestY = topSideY
                    bestX = freeNode.x
            if freeNode.width >= height and freeNode.height >= width:
                topSideY = freeNode.y + width
                if topSideY < bestY or (topSideY==bestY and freeNode.x<bestX):
                    bestNode.init(freeNode, height, width, True)
                    bestY = topSideY
                    bestX = freeNode.x
        return bestNode, bestY, bestX

    def find_position_bestshortsidefit(self, width, height):
        bestNode = Rect()
        bestShortSideFit = bestLongSideFit = sys.maxint
        for i, freeNode in enumerate(self.freeRectList):
            if freeNode.width >= width and freeNode.height >= height:
                leftoverHoriz = abs(freeNode.width - width)
                leftoverVert = abs(freeNode.height - height)
                shortSideFit = min(leftoverHoriz, leftoverVert)
                longSideFit = max(leftoverHoriz, leftoverVert)

                if shortSideFit < bestShortSideFit or \
                        ((shortSideFit==bestShortSideFit) and longSideFit<bestLongSideFit):
                    bestNode.init(freeNode, width, height)
                    bestShortSideFit = shortSideFit
                    bestLongSideFit = longSideFit
            if freeNode.width >= height and freeNode.height >= width:
                flippedLeftoverHoriz = abs(freeNode.width - height)
                flippedLeftoverVert = abs(freeNode.height - width)
                flippedShortSideFit = min(flippedLeftoverHoriz, flippedLeftoverVert)
                flippedLongSideFit = max(flippedLeftoverHoriz, flippedLeftoverVert)
                if flippedShortSideFit < bestShortSideFit or \
                        flippedShortSideFit == bestShortSideFit and flippedLongSideFit < bestLongSideFit:
                    bestNode.init(freeNode, height, width, True)
                    bestShortSideFit = flippedShortSideFit
                    bestLongSideFit = flippedLongSideFit
        return bestNode, bestShortSideFit, bestLongSideFit

    def find_position_bestlongsidefit(self, width, height):
        bestNode = Rect()
        bestLongSideFit = bestShortSideFit = sys.maxint
        for i, freeNode in enumerate(self.freeRectList):
            if freeNode.width >= width and freeNode.height >= height:
                leftoverHoriz = abs(freeNode.width - width)
                leftoverVert = abs(freeNode.height - height)
                shortSideFit = min(leftoverHoriz, leftoverVert)
                longSideFit = max(leftoverHoriz, leftoverVert)

                if longSideFit < bestLongSideFit or \
                        ((longSideFit==bestLongSideFit) and shortSideFit<bestShortSideFit):
                    bestNode.init(freeNode, width, height)
                    bestShortSideFit = shortSideFit
                    bestLongSideFit = longSideFit
            if freeNode.width >= height and freeNode.height >= width:
                flippedLeftoverHoriz = abs(freeNode.width - height)
                flippedLeftoverVert = abs(freeNode.height - width)
                flippedShortSideFit = min(flippedLeftoverHoriz, flippedLeftoverVert)
                flippedLongSideFit = max(flippedLeftoverHoriz, flippedLeftoverVert)
                if flippedLongSideFit < bestLongSideFit or \
                        flippedLongSideFit == bestLongSideFit and flippedShortSideFit < bestShortSideFit:
                    bestNode.init(freeNode, height, width, True)
                    bestShortSideFit = flippedShortSideFit
                    bestLongSideFit = flippedLongSideFit
        return bestNode, bestLongSideFit, bestShortSideFit

    def find_position_bestareafit(self, width, height):
        bestNode = Rect()
        bestAreaFit = bestShortSideFit = sys.maxint
        for i, freeNode in enumerate(self.freeRectList):
            areaFit = freeNode.width * freeNode.height - width * height
            if freeNode.width >= width and freeNode.height >= height:
                leftoverHoriz = abs(freeNode.width - width)
                leftoverVert = abs(freeNode.height - height)
                shortSideFit = min(leftoverHoriz, leftoverVert)
                if areaFit < bestAreaFit or \
                        areaFit == bestAreaFit and shortSideFit < bestShortSideFit:
                    bestNode.init(freeNode, width, height)
                    bestShortSideFit = shortSideFit
                    bestAreaFit = areaFit

            if freeNode.width >= height and freeNode.height >= width:
                leftoverHoriz = abs(freeNode.width - height)
                leftoverVert = abs(freeNode.height - width)
                shortSideFit = min(leftoverHoriz, leftoverVert)
                if areaFit < bestAreaFit or \
                        areaFit == bestAreaFit and shortSideFit < bestShortSideFit:
                    bestNode.init(freeNode, height, width, True)
                    bestAreaFit = areaFit
                    bestShortSideFit = shortSideFit
        return bestNode, bestAreaFit, bestShortSideFit

    def common_interval_len(self, i1start, i1end, i2start, i2end):
        if i1end < i2start or i2end < i1start:
            return 0
        return min(i1end, i2end) - max(i1start, i2start)

    def contact_point_score(self, x, y, width, height):
        score = 0
        if x == 0 or x + width == self.binWidth:
            score += height
        if y == 0 or y + height == self.binHeight:
            score += width
        for rect in self.usedRectList:
            if rect.x == x + width  or \
                    rect.x + rect.width == x:
                score += self.common_interval_len(rect.y, rect.y+rect.height, y, y+rect.height)
            if rect.y == y + height or \
                    rect.y + rect.height == y:
                score += self.common_interval_len(rect.x, rect.x+rect.width, x, x+width)
        return score

    def find_position_contactpoint(self, width, height):
        bestNode = Rect()
        bestContactScore = -1
        for i, freeNode in enumerate(self.freeRectList):
            if freeNode.width >= width and freeNode.height >= height:
                score = self.contact_point_score(freeNode.x, freeNode.y, width, height)
                if score > bestContactScore:
                    bestNode.init(freeNode, width, height)
                    bestContactScore = score
            if freeNode.height >= width and freeNode.width >= height:
                score = self.contact_point_score(freeNode.x, freeNode.y, height, width)
                if score > bestContactScore:
                    bestNode.init(freeNode, height, width, True)
                    bestContactScore = score
        return bestNode, -bestContactScore, 0

    def split_free_rect(self, freeNode, usedNode):
        if ((usedNode.x >= freeNode.x + freeNode.width) or
            (usedNode.x + usedNode.width <= freeNode.x) or
            (usedNode.y >= freeNode.y + freeNode.height) or
            (usedNode.y + usedNode.height <= freeNode.y)):
            return False

        if ((usedNode.x < freeNode.x + freeNode.width) and (usedNode.x + usedNode.width > freeNode.x)):
            if ((usedNode.y > freeNode.y) and (usedNode.y < freeNode.y + freeNode.height)):
                newNode = deepcopy(freeNode)
                newNode.height = usedNode.y - newNode.y
                self.freeRectList.append(newNode)
            if ((usedNode.y + usedNode.height) < (freeNode.y + freeNode.height)):
                newNode = deepcopy(freeNode)
                newNode.y = usedNode.y + usedNode.height
                newNode.height = freeNode.y + freeNode.height - (usedNode.y + usedNode.height)
                self.freeRectList.append(newNode)
        if ((usedNode.y < freeNode.y + freeNode.height) and (usedNode.y + usedNode.height > freeNode.y)):
            if ((usedNode.x > freeNode.x) and  (usedNode.x < freeNode.x + freeNode.width)):
                newNode = deepcopy(freeNode)
                newNode.width = usedNode.x - newNode.x
                self.freeRectList.append(newNode)

            if ((usedNode.x + usedNode.width) < (freeNode.x + freeNode.width)):
                newNode = deepcopy(freeNode)
                newNode.x = usedNode.x + usedNode.width
                newNode.width = freeNode.x + freeNode.width - (usedNode.x + usedNode.width)
                self.freeRectList.append(newNode)
        return True

    def prune_free_rect_list(self):
        del_index_list = []
        for i, node_1 in enumerate(self.freeRectList):
            if i in del_index_list:
                continue
            for j, node_2 in enumerate(self.freeRectList[i+1:]):
                if j in del_index_list:
                    continue
                if self.is_containedin(node_1, node_2):
                    del_index_list.append(i)
                else:
                    if self.is_containedin(node_2, node_1):
                        del_index_list.append(j)
        tmp_list = self.freeRectList
        self.freeRectList = []
        for i, node in enumerate(tmp_list):
            if i not in del_index_list:
                self.freeRectList.append(node)

    def is_containedin(self, rect_small, rect_big):
        return rect_small.x >= rect_big.x and rect_small.y >= rect_big.y \
            and rect_small.x + rect_small.width <= rect_big.x + rect_big.width \
            and rect_small.y + rect_small.height <= rect_big.y + rect_big.height

    def occupancy(self):
        usedSurfaceArea = 0
        for i in self.usedRectList:
            usedSurfaceArea += i.width * i.height
        return (usedSurfaceArea * 1.0)/ (self.binWidth * self.binHeight)

class ImageNode(object):
    def __init__(self, path, image):
        self.path = path
        self.image = image
        self.node = None

    @property
    def width(self):
        return self.image.size[0]

    @property
    def height(self):
        return self.image.size[1]

    @property
    def position(self):
        return self.node.x, self.node.y

if __name__ == "__main__":
    import argparse
    from glob import iglob
    import os
    from PIL import Image
    _epilog = "example: python maxrect.py images_file_dir output.png"
    parser = argparse.ArgumentParser(epilog=_epilog)
    #parser.add_argument("width", type=int, help="the max width of output file")
    #parser.add_argument("height", type=int, help="the max height of output file")
    parser.add_argument("src", type=str, help="src directory")
    parser.add_argument("dst", type=str, help="dest png file")
    args = parser.parse_args()
    names_list = iglob(os.path.join(args.src, "*.png"))
    image_dict = {}
    rect_max_len = 0
    all_rect_area = 0
    for name in names_list:
        image = Image.open(name)
        all_rect_area += image.size[0] * image.size[1]
        t = max(image.size[0], image.size[1])
        rect_max_len = t if t > rect_max_len else rect_max_len
        image_dict[name] = ImageNode(name, image)
    fun_name = 'contactpoint'
    bin = PackBin()
    #for fun_name in ['bottomleft', 'shortsidefit', 'longsidefit', 'areafit', 'contactpoint']:
    #try to get the fit width and height
    fit_area = all_rect_area * 1.2
    t = int(math.sqrt(fit_area))
    fit_height = rect_max_len if rect_max_len > t else t
    fit_width = int(all_rect_area / fit_height)
    while True:
        print fit_height, fit_width
        for node in image_dict.itervalues():
            node.node = None
        bin.init(fit_width, fit_height)
        try:
            bin.insert_offline(image_dict, fun_name)
        except Exception as e:
            print e
            fit_width = fit_width + 10
            #fit_height = int(fit_height * 1.1)
            continue
        output_image_offline = Image.new("RGBA", (fit_width, fit_height))
        for imagenode in image_dict.itervalues():
            packedRect = imagenode.node
            #print("Packed to (x,y)=(%d,%d), (w,h)=(%d,%d). Free space left: %.2f%%\n"%(
            #    packedRect.x, packedRect.y, packedRect.width, packedRect.height, 100.0 - bin.occupancy()*100.0))
            image = imagenode.image.transpose(Image.ROTATE_90) if packedRect.rotation_flag else imagenode.image
            output_image_offline.paste(image, imagenode.position)
        break
    print "Free space left %2f%%"%(100.0 - bin.occupancy()*100.0)
    output_image_offline.save(fun_name+args.dst, "PNG")
