#!/usr/bin/env python3
r"""
Script designed to take a TIFF stack and determine the vertical offset of
the fracture.
"""
from itertools import product
from PIL import Image
import time
import scipy as sp
from scipy import sparse as sprs
from scipy.sparse import csgraph

#
# explicit del statments are being used until I make this more
# function based, since the arrays can be quite large and currently never
# go out of scope to be cleaned up automatically
#


# loading image
print('loading image...')
st = time.time()
image_file = 'is6-turn1-binary-fracture.tif'
img_data = Image.open(image_file)
# getting image dimensions
x_dim, y_dim = img_data.size
z_dim = img_data.n_frames
print('    image dimensions: ', x_dim, y_dim, z_dim)
print('    ==> {} seconds'.format(time.time() - st))


# creating full image array
print('creating image array...')
st = time.time()
data_array = []
for frame in range(z_dim):
    img_data.seek(frame)
    frame = sp.array(img_data, dtype=bool).transpose()
    frame = ~frame  # beacuse fracture is black, solid is white
    data_array.append(frame)
del img_data
del frame
print('    ==> {} seconds'.format(time.time() - st))

# creating data vector
print('flatting array and locating non-zero voxels...')
st = time.time()
data_array = sp.stack(data_array, axis=2)
data_vector = sp.ravel(data_array)
nonzero_locs = sp.where(data_vector)[0]
print('    {} non-zero voxels'.format(nonzero_locs.size))
print('    ==> {} seconds'.format(time.time() - st))

# mapping i,j,k coordinates of data vector
print('creating i,j,k index map of non-zero values...')
st = time.time()
index_map = sp.unravel_index(nonzero_locs, data_array.shape)
index_map = sp.stack(index_map, axis=1)
del data_vector
print('    ==> {} seconds'.format(time.time() - st))

# creating connections array based on 26 point connectivity
print('generating network connections...')
st = time.time()
conn_map = list(product([0, -1, 1], [0, -1, 1], [0, -1, 1]))
conn_map = sp.array(conn_map, dtype=int)
conn_map = conn_map[1:]
#
slice_list = [slice(0, 10000)]
for i in range(slice_list[0].stop, index_map.shape[0], slice_list[0].stop):
    slice_list.append(slice(i, i+slice_list[0].stop))
slice_list[-1] = slice(slice_list[-1].start, index_map.shape[0])
#
conns = sp.ones((0, 2), dtype=sp.uint32)
print('    number of slices to process: ', len(slice_list))
for sect in slice_list:
    # setting up index array, last index is central node neighbors connect to
    nodes = index_map[sect]
    inds = sp.repeat(nodes, 26, axis=0) + sp.tile(conn_map, (nodes.shape[0], 1))
    nodes = sp.ravel_multi_index(sp.hsplit(nodes, 3), (x_dim, y_dim, z_dim))
    inds = sp.hstack([inds, sp.repeat(nodes, 26, axis=0)])
    # removing negative indicies
    mask = ~inds[:, 0:3] < 0
    inds = inds[sp.sum(mask, axis=1) == 3]
    # removing indicies outside of bounds
    mask = (inds[:, 0] < x_dim, inds[:, 1] < y_dim, inds[:, 2] < z_dim)
    mask = sp.stack(mask, axis=1)
    inds = inds[sp.sum(mask, axis=1) == 3]
    # removing indices with zero-weight connection
    mask = data_array[inds[:, 0], inds[:, 1], inds[:, 2]]
    inds = inds[mask]
    if inds.size:
        # calculating flattened index and appending to conns array
        nodes = sp.ravel_multi_index(sp.hsplit(inds[:, 0:3], 3), (x_dim, y_dim, z_dim))
        inds = sp.hstack([sp.reshape(inds[:, -1], (inds.shape[0], 1)), nodes])
        inds[inds[:, 0] > inds[:, 1]] = inds[inds[:, 0] > inds[:, 1]][:, ::-1]
        conns = sp.append(conns, inds.astype(sp.uint32), axis=0)
#
del index_map
del nodes
del inds
del mask
print('    ==> {} seconds'.format(time.time() - st))

# using scipy magic from stackoverflow to remove dupilcate connections
print('removing duplicate connections...')
st = time.time()
orig = conns.shape[0]
conns = sp.ascontiguousarray(conns)
dtype = sp.dtype((sp.void, conns.dtype.itemsize*conns.shape[1]))
conns = sp.unique(conns.view(dtype)).view(conns.dtype).reshape(-1, conns.shape[1])
print('    removed {} duplicates'.format(orig - conns.shape[0]))
print('    ==> {} seconds'.format(time.time() - st))

# determining local index of values in conns array
print('re-indexing connections array to be relative to non-zero values...')
st = time.time()
mapper = -sp.ones(nonzero_locs[-1]+1)
mapper[nonzero_locs] = sp.arange(nonzero_locs.size, dtype=sp.uint32)
conns[:, 0] = mapper[conns[:, 0]]
conns[:, 1] = mapper[conns[:, 1]]
del mapper
print('    ==> {} seconds'.format(time.time() - st))


print('creatinadjacentcy matrix...')
st = time.time()
# creating adjacency matrix
num_blks = nonzero_locs.size
row = sp.append(conns[:, 0], conns[:, 1])
col = sp.append(conns[:, 1], conns[:, 0])
weights = sp.ones(conns.size)  # using size automatically multiplies by 2
#
# Generate sparse adjacency matrix in 'coo' format and convert to csr
adj_mat = sprs.coo_matrix((weights, (row, col)), (num_blks, num_blks))
adj_mat = adj_mat.tocsr()
print('    ==> {} seconds'.format(time.time() - st))

# identifying small disconnected clusters
print('determining connected components...')
st = time.time()
num_cs, cs_ids = csgraph.connected_components(csgraph=adj_mat,directed=False)


print(num_cs, num_blks)
del adj_mat
print('    ==> {} seconds'.format(time.time() - st))



time.sleep(5)


