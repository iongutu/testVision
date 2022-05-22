import random
import numpy as np
import itertools
import cv2
import os
from skimage.measure import label, regionprops, find_contours

# get all permutation from a list
def get_all_n_permutation(my_list, n):
    return list(itertools.permutations(my_list, n))


# arguments are the coordinats of two rectangles
def is_inside(x11, y11, x12, y12, x21, y21, x22, y22):
    return x11 <= x21 <= x22 <= x12 and y11 <= y21 <= y22 <= y12


# get border around contours of mask
def get_mask_border(mask):
    h, w = mask.shape
    # create an array the same size as mask
    border = np.zeros((h, w))
    contours = find_contours(mask, fully_connected='high', positive_orientation='high')
    for contour in contours:
        # get coordinate of a contour
        for data in contour:
            x = int(data[0])
            y = int(data[1])
            border[x][y] = 255

    return border


# get points of rectangles around borders
def border_to_rectangle(mask):
    rectangles = []
    # label conected region of contours
    labels = label(get_mask_border(mask))
    # get proprieties of a labeled region to draw a rectangle
    proprieties = regionprops(labels)
    for prop in proprieties:
        rectangles.append([prop.bbox[1], prop.bbox[0], prop.bbox[3], prop.bbox[2]])

    return rectangles


# add aditional dimention to concatenate with original image(for a better comparation)
def add_mask_next(mask):
    mask = np.expand_dims(mask, axis=-1)
    mask = np.concatenate([mask, mask, mask], axis=-1)

    return mask


if __name__ == "__main__":
    root = "DATA"
    images = list(sorted(os.listdir(os.path.join(root, "image"))))
    masks = list(sorted(os.listdir(os.path.join(root, "label"))))

    # loop over the dataset
    for image_name, mask_name in zip(images, masks):
        # read image and correspondig semantic mask
        image = cv2.imread(root + '\\image\\' + image_name)
        # read mask in grayscale, because we can easy work with segmentation masks
        mask_initial = cv2.imread(root + '\\label\\' + mask_name, cv2.IMREAD_GRAYSCALE)
        # calculate histogram of mask to see distribution of colors (potential objects)
        histogram = cv2.calcHist([mask_initial], [0], None, [256], [0, 256])
        # add all colors from mask in an array, and also save color with max freq(this is in many case background data)
        color = []
        maxFreq = 0
        value = 0
        for i in range(0, len(histogram)):
            # at least 10 pixel of same color as an empiric parameter
            if histogram[i][0] > 10 and i != 0:
                if int(histogram[i][0]) > maxFreq:
                    maxFreq = int(histogram[i][0])
                    value = i
                color.append(i)
        color.remove(value)

        # chose a random color which represent a random object/s
        random_color = random.choice(color)

        # extract one random color from mask
        mask = cv2.inRange(mask_initial, random_color, random_color)
        rectangles = border_to_rectangle(mask)
        # if we have more than 20 rectangles, most probably  something is not ok too many object of same class
        while len(rectangles) >= 20:
            random_color = random.choice(color)
            # extract another random color from mask
            mask = cv2.inRange(mask, random_color, random_color)
            rectangles = border_to_rectangle(mask)

        ''' This part of code get biggest rectangle and delete from them all other rectangles
            Implementation was made to avoid detecting another contour inside another one and
            misclassified objects as belong to same class 
        '''
        # find the biggest rectangle
        # max = 0
        # max_box = 0
        # for i in range(0, len(rectangles)):
        #     if max < rectangle_area(rectangles[i][0], rectangles[i][1], rectangles[i][2], rectangles[i][3]):
        #         max = rectangle_area(rectangles[i][0], rectangles[i][1], rectangles[i][2], rectangles[i][3])
        #         max_box = i
        #
        # cv2.rectangle(image, (rectangles[max_box][0], rectangles[max_box][1]), (rectangles[max_box][2], rectangles[max_box][3]), (0, 255, 0), 1)
        # for i in range(0, len(rectangles)):
        #     if i != max_box:
        #         if not (is_inside(rectangles[max_box][0], rectangles[max_box][1], rectangles[max_box][2], rectangles[max_box][3], \
        #                 rectangles[i][0], rectangles[i][1], rectangles[i][2], rectangles[i][3])):
        #             x = cv2.rectangle(image, (rectangles[i][0], rectangles[i][1]), (rectangles[i][2], rectangles[i][3]), (0, 255, 0), 1)

        '''
            Better approch is to verify rectangles two by two and remove those inside other to avoid
           detecting another contour inside another one and misclassified objects as belong to same class.
        '''

        proposed_to_delete = []
        for box1, box2 in get_all_n_permutation(rectangles, 2):
            # if smaller rectangle is inside the bigger one, don't draw because is a contour problem
            if (is_inside(box1[0], box1[1], box1[2], box1[3],
                          box2[0], box2[1], box2[2], box2[3])):
                if box2 not in proposed_to_delete:
                    proposed_to_delete.append(box2)

        for box_to_delete in proposed_to_delete:
            rectangles.remove(box_to_delete)
        for box in rectangles:
            cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 1)

        # concatenate labeled image with coresponding mask
        cat_image = np.concatenate([image, add_mask_next(mask)], axis=1)
        if not os.path.exists("results"):
            os.makedirs("results")
        # write result to specified folder.
        cv2.imwrite("results//" + str(image_name), cat_image)
