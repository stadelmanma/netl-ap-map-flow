#!/usr/bin/env python3
r"""
Script designed to take a TIFF stack and determine the vertical offset of
the fracture.
"""
from PIL import Image
import scipy as sp
from scipy import sparse as sprs

# loading image
print('loading image...')
image_file = 'is6-turn1-binary-fracture.tif'
img_data = Image.open(image_file)

# getting image dimensions
x_dim, y_dim = img_data.size
n_frames = img_data.n_frames

# creating full image array
print('creating image array...')
data_array = []
for frame in range(n_frames):
    img_data.seek(frame)
    frame = sp.array(img_data, dtype=bool)
    frame = ~frame # beacuse fracture is black, solid is white
    data_array.append(frame.astype(int))
#
# creating data vector is index map to get i,j,k coordinates from
print('flatting array and locating non-zero voxels')
data_array = sp.stack(data_array, axis=2)
data_vector = sp.ravel(data_array)
nonzero_vector = sp.where(data_vector)[0]

print('creating i,j,k index map of non-zero values')
index_map = sp.unravel_index(nonzero_vector, data_array.shape)
index_map = sp.stack(index_map, axis=1)

#
# need to define block connectivity here using all 26 surrounding blocks
# instead of just the 4 used in DataField, face-face, edge-edge, corner-corner.
# handling duplicates would make the final size much smaller but may be more
# expensive than just letting it go. Store flattened indicies and use those
# in conjunction with data_vector to arrive at the weights for the adjacency matrix
#