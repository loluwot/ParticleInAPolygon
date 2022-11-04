import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import alphashape
from descartes import PolygonPatch
def to_poly(im_name):
    im = cv.imread(im_name, cv.IMREAD_UNCHANGED)
    im[im[:,:,3] == 0] = [255, 255, 255, 255]
    im = im[:, :, :3]
    im = cv.threshold(im, 127, 255, cv.THRESH_BINARY)[1]

    ps = np.argwhere(im[:, :, 0] != 255).astype(np.float32)
    mi_x, ma_x = np.min(ps[:, 0]), np.max(ps[:, 0])
    mi_y, ma_y = np.min(ps[:, 1]), np.max(ps[:, 1])
    ps[:, 0] = (ps[:, 0] - mi_x)/(ma_x - mi_x)
    ps[:, 1] = (ps[:, 1] - mi_y)/(ma_y - mi_y)
    ps = ps[:, ::-1]
    ps[:, 1] = 1-ps[:, 1]

    alpha_shape = alphashape.alphashape(ps, 2).normalize() #concave hull
    # fig, ax = plt.subplots()
    # # # ax.scatter(*zip(*ps))
    # ax.add_patch(PolygonPatch(alpha_shape, alpha=0.2))
    # plt.show()
    return alpsha_shape.exterior.coords

# to_poly('trollface.png')