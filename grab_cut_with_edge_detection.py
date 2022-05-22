import random
import numpy as np
import itertools
import cv2
import os
from skimage.measure import label, regionprops, find_contours

# hyperparameter used to denote # of iteration for GRABCUT algo.
ITER = 25


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
    count = 1
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

        # allocate memory for two arrays that the GrabCut algorithm uses for foreground and background
        fgModel = np.zeros((1, 65), dtype="float")
        bgModel = np.zeros((1, 65), dtype="float")
        # any mask values greater than zero should be set to probable foreground, and equal to zero to background
        mask[mask > 0] = cv2.GC_PR_FGD
        mask[mask == 0] = cv2.GC_BGD
        # apply GrabCut using the the mask segmentation method
        (mask, bgModel, fgModel) = cv2.grabCut(image, mask, None, bgModel,
                                               fgModel, iterCount=ITER, mode=cv2.GC_INIT_WITH_MASK)

        print("Processed:" + str(count))
        count += 1
        # set all definite background and probable background pixels to 0
        # while definite foreground and probable foreground pixels are set to 0
        outputMask = np.where((mask == cv2.GC_BGD) | (mask == cv2.GC_PR_BGD), 0, 1)

        outputMask = np.uint16(outputMask)
        # use gaussian blur  remove inside small points (can use a median blur to keep edgess intact)
        # but after tests not matter
        outputMask = cv2.GaussianBlur(outputMask, (5, 5), 0)
        # if output mask contain only background object (mask will be fully black)
        # than we prefer to add object from possible background and give apposite annotation
        # pixel from probable background set to one other set to 0 in this case we keep selected object in mask white
        if cv2.countNonZero(outputMask) == 0:
            # use negative as object will be with white on image,
            outputMask = np.where((mask == cv2.GC_PR_BGD), 1, 0)

        # scale the output_Mask
        outputMask = (outputMask * 255).astype("uint8")
        # get rectangles from mask
        rectangles = border_to_rectangle(outputMask)

        '''
           Better approch is to verify rectangles two by two and remove those inside other to avoid
           detecting another contour inside another one and misclassified objects as belong to same class.
        '''
        # if smaller rectangle is inside the bigger one, don't draw because is a contour problem
        proposed_to_delete = []
        for box1, box2 in get_all_n_permutation(rectangles, 2):
            if (is_inside(box1[0], box1[1], box1[2], box1[3],
                          box2[0], box2[1], box2[2], box2[3])):

                if box2 not in proposed_to_delete:
                    proposed_to_delete.append(box2)

        for box_to_delete in proposed_to_delete:
            rectangles.remove(box_to_delete)

        for bbox in rectangles:
            cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 1)

        # concatenate labeled image with coresponding mask
        cat_image = np.concatenate([image, add_mask_next(outputMask)], axis=1)
        if not os.path.exists("results"):
            os.makedirs("results")
        cv2.imwrite("results//" + str(image_name), cat_image)
