#this utilizes the Image class of PIL version 1.1.7, for list of dependencies see README
import Image
import ImageFilter #must not use ImageFilter.FIND_EDGES. must re-invent wheel. grrrr.
from math import degrees, atan, sqrt

#note to self: this should probably just be inheriting from the Image object and adding a couple of methods to it, maybe rewrite later
class ImageIndexer(object):
    "open images from file and produce histogram and edgemap index for the image"
    def __init__(self, filename):
        self.img = Image.open(filename)
        self.name = filename

    def getImgInfo(self):
        print "format = %s, size = %s, mode = %s" %(self.img.format, self.img.size, self.img.mode)

    def makeGrayscale(self):
        if self.img.mode != "L":
            self.img = self.img.convert("L")

    def makeHistogram(self):
        "returns a 16 bin histogram of the image"
        hist = {}
        vals_vector = list(self.img.getdata())
        for value in vals_vector:
            key = value%16
            if key not in hist:
                hist[key] = 1
            else:
                hist[key] += 1
        return hist

    def makeEdgeMap(self):
        "returns an edge map found by Canny edge detection"
        temp_img = self.img.filter(ImageFilter.BLUR) #first apply Gaussian blur to denoise image
        temp_img = crop_img(temp_img, 3) #crops the image so that its height and width are multiples of n, 3 in this case
        temp_img_data = list(temp_img.getdata())
        edge_map = Image.new(temp_img.mode, temp_img.size)
        edge_map_data = [] #initially empty, this will be built up as we go
        width = temp_img.size[0]
        height = temp_img.size[1]
        #second step is to apply non-maximum suppression using a 3x3 mask
        for rownum in range(1, height, 3): #traverse rows from top to bottom, by 3s, start at row 1 
            for i in range(1, width, 3): #traverse across row from left to right, by 3s, start at column 1
                cur_mask = get_mask(temp_img_data, width, rownum, i) #function returns a 3x3 mask centered on pixel i
                grad_x = get_x_gradient(cur_mask) #function returns a scalar that is the x direction gradient of the mask
                grad_y = get_y_gradient(cur_mask) #function returns a scalar that is the y direction gradient of the mask
                edge_strength = int(math.sqrt(grad_x*grad_x + grad_y*grad_y))
                if edge_strength > 255:
                    edge_strength = 255
                edge_direction_angle = math.degrees(math.atan2(grad_y, grad_x))
                edge_mask = get_edge_mask(edge_direction_angle, edge_strength) #returns a 3x3 mask in the appropriate direction and strength
        #third step is double threshold hysteresis this is pure magic to me, research more
        hysteresis(low, high, abra_cadabra, pixie_dust)
        write_mask(edge_map_data, i, edge_mask) 
        #finish up
        edge_map.putdata(edge_map_data)
        edge_map.save(filename+"_edgemap", self.img.format)

    def crop_img(self, img, n):
        "crops an image so that its width and height are multiples of n, note: this causes a small amount of data loss as the cropped image is slightly smaller"
        width = img.size[0]
        height = img.size[1]
        new_width = width - width%n
        new_height = height - height%n
        cropped_img = Image.new(img.mode, (new_width, new_height))
        cropped_img = img.crop((0, 0, new_width, new_height))
        return cropped_img

    def get_mask(self, img_data, width, rownum, i):
        "returns a 3x3 mask centered on pixel i"
        mask = [0]*9
        mask[0] = img_data[(rownum*width-1) + (i-1)]
        mask[1] = img_data[(rownum*width-1) + i]
        mask[2] = img_data[(rownum*width-1) + (i+1)]
        mask[3] = img_data[(rownum*width) + (i-1)]
        mask[4] = img_data[(rownum*width) + i]
        mask[5] = img_data[(rownum*width) + (i+1)]
        mask[6] = img_data[(rownum*width+1) + (i-1)]
        mask[7] = img_data[(rownum*width+1) + i]
        mask[8] = img_data[(rownum*width+1) + (i+1)]
        return mask

    def get_x_gradient(self, mask):
        "gets the scalar gradient with respect to X direction of the 3x3 mask using the Sobel Operator"
        grad_matrix = [-1, 0, 1, -2, 0, 2, -1, 0, 1]
        sum = 0
        for i in range(9):
            sum += mask[i]*grad_matrix[i]
        return sum

    def get_y_gradient(self, mask):
        "gets the scalar gradient with respect to Y direction of the 3x3 mask using the Sobel Operator"
        grad_matrix = [1, 2, 1, 0, 0, 0, -1, -2, -1]
        sum = 0
        for i in range(9):
            sum += mask[i]*grad_matrix[i]
        return sum

    def get_edge_mask(self, angle, strength):
        "gets the 3x3 edge mask that corresponds to the given angle and strength"
        #there are 4 possible masks that can be given here, based on angle
        #they are: up<->down, left<->right, top-left<->bottom-right, top-right<->bottom-left
        if (-22.5 < angle <= 22.5) or (157.5 < angle <= 180) or (-157.5 >= angle >= -180):
            edge_mask = [0, 0, 0, strength, strength, strength, 0, 0, 0]
        if (22.5 < angle <= 67.5) or (-112.5 >= angle > -157.5):
            edge_mask = [0, 0, strength, 0, strength, 0, strength, 0, 0]
        if (67.5 < angle <= 112.5) or (-67.5 >= angle > -112.5):
            edge_mask = [0, strength, 0, 0, strength, 0, 0, strength, 0]
        if (112.5 < angle <= 157.5) or (-22.5 >= angle > -67.5):
            edge_mask = [strength, 0, 0, 0, strength, 0, 0, 0, strength]
        return edge_mask

         


        







