#!/usr/bin/env python3
r"""
Script designed to take a TIFF stack and determine the vertical offset of
the fracture.
"""
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
from glob import glob
from itertools import product
from logging import DEBUG
from PIL import Image
import os
import scipy as sp
from scipy import sparse as sprs
from scipy.sparse import csgraph
from scipy.interpolate import griddata
from ApertureMapModelTools import _get_logger

#
desc_str = r"""
Description: Generates a 2-D offset map based on the binary CT image stack.
The offset map is based on the lower surface of the fracture after removing
disconnected clusters and noise. Gaps in the data from zero aperture regions
are interpolated based on the nearest neighbor.

Written By: Matthew stadelman
Date Written: 2016/08/30
Last Modfied: 2016/09/06
"""
# setting up logger
logger = _get_logger('ApertureMapModelTools.Scripts')

# creating arg parser
parser = argparse.ArgumentParser(description=desc_str, formatter_class=RawDesc)

# adding arguments
parser.add_argument('-f', '--force', action='store_true',
                    help='allows program to overwrite existing files')

parser.add_argument('-v', '--verbose', action='store_true',
                    help='debug messages are printed to the screen')

parser.add_argument('-o', '--output-dir',
                    type=os.path.realpath, default=os.getcwd(),
                    help='''outputs files to the specified
                    directory, sub-directories are created as needed''')

parser.add_argument('-n', '--num-clusters', type=int, default=5,
                    help='number of clusters to retain, ordered by size')

parser.add_argument('image_file', type=os.path.realpath,
                    help='binary TIF stack image to process')

parser.add_argument('offset_map_name',
                    help='name to save the offset map under')

parser.add_argument('img_stack_dirname', nargs='?', default=None,
                    help='''directory to save processed image stack to,
                    if omitted the stack is not saved''')


def apm_calculate_offset_map():
    r"""
    Driver program to load an image and generate an offset map. Arrays
    can be quite large and are explicity deleted to conserve RAM
    """
    # parsing commandline args
    namespace = parser.parse_args()
    if namespace.verbose:
        logger.setLevel(DEBUG)
    print(namespace)

    # checking paths
    stack_path = os.path.join(namespace.output_dir, namespace.img_stack_dirname)
    map_path = os.path.join(namespace.output_dir, namespace.offset_map_name)
    #
    if os.path.exists(stack_path) and not namespace.force:
        msg = 'Image Stack directory: {} already exists, '
        msg += 'use "-f" option to overwrite'
        raise FileExistsError(msg.format(stack_path))
    if os.path.exists(map_path) and not namespace.force:
        msg = '{} already exists, use "-f" option to overwrite'
        raise FileExistsError(msg.format(map_path))

    # loading image data
    data_array = load_image_data(namespace.image_file)
    img_dims = data_array.shape
    nonzero_locs = locate_nonzero_data(data_array)
    index_map = generate_index_map(nonzero_locs, img_dims)

    # determing connectivity and removing clusters
    conns = generate_node_connectivity_array(index_map, data_array)
    del data_array
    del index_map
    nonzero_locs = remove_isolated_clusters(conns,
                                            nonzero_locs,
                                            namespace.num_clusters)

    # saving processed image
    if namespace.img_stack_dirname is not None:
        save_image_stack(nonzero_locs, img_dims, stack_path)

    # creating offset map and filling gaps left from zero aperture regions
    offset_map = generate_offset_map(nonzero_locs, img_dims)
    offset_map = patch_holes(offset_map)

    # saving map
    sp.savetxt(map_path, offset_map.T, fmt='%d', delimiter='\t')


def load_image_data(image_file):
    r"""
    Loads an image from a *.tiff stack and creates an array from it. The
    fracture is assumed to be black and the solid is white.
    """
    logger.info('loading image...')
    img_data = Image.open(image_file)
    #
    # creating full image array
    logger.info('creating image array...')
    data_array = []
    for frame in range(img_data.n_frames):
        img_data.seek(frame)
        frame = sp.array(img_data, dtype=bool).transpose()
        frame = ~frame  # beacuse fracture is black, solid is white
        data_array.append(frame)
    #
    data_array = sp.stack(data_array, axis=2)
    logger.debug('    image dimensions: {} {} {}'.format(*data_array.shape))
    #
    return data_array


def locate_nonzero_data(data_array):
    r"""
    Generates a vector of non-zero indicies for the flattened array
    """
    #
    logger.info('flatting array and locating non-zero voxels...')
    data_vector = sp.ravel(data_array)
    nonzero_locs = sp.where(data_vector)[0]
    logger.debug('    {} non-zero voxels'.format(nonzero_locs.size))
    #
    return nonzero_locs


def generate_index_map(nonzero_locs, shape):
    r"""
    Determines the i,j,k indicies of the flattened array
    """
    #
    logger.info('creating index map of non-zero values...')
    index_map = sp.unravel_index(nonzero_locs, shape)
    index_map = sp.stack(index_map, axis=1)
    #
    return index_map


def generate_node_connectivity_array(index_map, data_array):
    r"""
    Generates a node connectivity array based on faces, edges and corner
    adjacency
    """
    #
    logger.info('generating network connections...')
    #
    # setting up some constants
    x_dim, y_dim, z_dim = data_array.shape
    conn_map = list(product([0, -1, 1], [0, -1, 1], [0, -1, 1]))
    conn_map = sp.array(conn_map, dtype=int)
    conn_map = conn_map[1:]
    #
    # creating slice list to process data chunks
    slice_list = [slice(0, 10000)]
    for i in range(slice_list[0].stop, index_map.shape[0], slice_list[0].stop):
        slice_list.append(slice(i, i+slice_list[0].stop))
    slice_list[-1] = slice(slice_list[-1].start, index_map.shape[0])
    #
    conns = sp.ones((0, 2), dtype=sp.uint32)
    logger.debug('    number of slices to process: {}'.format(len(slice_list)))
    for sect in slice_list:
        # getting coordinates of nodes and their neighbors
        nodes = index_map[sect]
        inds = sp.repeat(nodes, conn_map.shape[0], axis=0)
        inds += sp.tile(conn_map, (nodes.shape[0], 1))
        #
        # calculating the flattened index of the central nodes and storing
        nodes = sp.ravel_multi_index(sp.hsplit(nodes, 3), data_array.shape)
        inds = sp.hstack([inds, sp.repeat(nodes, conn_map.shape[0], axis=0)])
        #
        # removing neigbors with negative indicies
        mask = ~inds[:, 0:3] < 0
        inds = inds[sp.sum(mask, axis=1) == 3]
        # removing neighbors with indicies outside of bounds
        mask = (inds[:, 0] < x_dim, inds[:, 1] < y_dim, inds[:, 2] < z_dim)
        mask = sp.stack(mask, axis=1)
        inds = inds[sp.sum(mask, axis=1) == 3]
        # removing indices with zero-weight connection
        mask = data_array[inds[:, 0], inds[:, 1], inds[:, 2]]
        inds = inds[mask]
        if inds.size:
            # calculating flattened index of remaining nieghbor nodes
            nodes = sp.ravel_multi_index(sp.hsplit(inds[:, 0:3], 3),
                                         data_array.shape)
            inds = sp.hstack([sp.reshape(inds[:, -1], (-1, 1)), nodes])
            # ensuring conns[0] is always < conns[1] for duplicate removal
            mask = inds[:, 0] > inds[:, 1]
            inds[mask] = inds[mask][:, ::-1]
            # appending section connectivity data to conns array
            conns = sp.append(conns, inds.astype(sp.uint32), axis=0)
    #
    # using scipy magic from stackoverflow to remove dupilcate connections
    logger.info('removing duplicate connections...')
    dim0 = conns.shape[0]
    conns = sp.ascontiguousarray(conns)
    dtype = sp.dtype((sp.void, conns.dtype.itemsize*conns.shape[1]))
    dim1 = conns.shape[1]
    conns = sp.unique(conns.view(dtype)).view(conns.dtype).reshape(-1, dim1)
    logger.debug('    removed {} duplicates'.format(dim0 - conns.shape[0]))
    #
    return conns


def generate_adjacency_matrix(conns, nonzero_locs):
    r"""
    generates a ajacency matrix based on connectivity array
    """
    msg = 're-indexing connections array from absolute to relative indicies'
    logger.info(msg)
    mapper = -sp.ones(nonzero_locs[-1]+1)
    mapper[nonzero_locs] = sp.arange(nonzero_locs.size, dtype=sp.uint32)
    conns[:, 0] = mapper[conns[:, 0]]
    conns[:, 1] = mapper[conns[:, 1]]
    del mapper
    #
    logger.info('creating adjacency matrix...')
    num_blks = nonzero_locs.size
    row = sp.append(conns[:, 0], conns[:, 1])
    col = sp.append(conns[:, 1], conns[:, 0])
    weights = sp.ones(conns.size)  # using size automatically multiplies by 2
    #
    # Generate sparse adjacency matrix in 'coo' format and convert to csr
    adj_mat = sprs.coo_matrix((weights, (row, col)), (num_blks, num_blks))
    adj_mat = adj_mat.tocsr()
    #
    return adj_mat


def remove_isolated_clusters(conns, nonzero_locs, num_to_keep):
    r"""
    Identifies and removes all disconnected clusters except the number of
    groups specified by "num_to_keep". num_to_keep=N retains the N largest
    clusters
    """
    #
    adj_mat = generate_adjacency_matrix(conns, nonzero_locs)
    #
    logger.info('determining connected components...')
    cs_ids = csgraph.connected_components(csgraph=adj_mat, directed=False)[1]
    groups, counts = sp.unique(cs_ids, return_counts=True)
    order = sp.argsort(counts)[::-1]
    groups = groups[order]
    counts = counts[order]
    #
    msg = '    {} component groups for {} total nodes'
    logger.debug(msg.format(groups.size, cs_ids.size))
    msg = '    largest group number: {}, size {}'
    logger.debug(msg.format(groups[0], counts[0]))
    msg = '    {} % of nodes contained in largest group'
    logger.debug(msg.format(counts[0]/cs_ids.size*100))
    msg = '    {} % of nodes contained in {} retained groups'
    num = sp.sum(counts[0:num_to_keep])/cs_ids.size*100
    logger.debug(msg.format(num, num_to_keep))
    #
    inds = sp.where(sp.in1d(cs_ids, groups[0:num_to_keep]))[0]
    num = nonzero_locs.size
    nonzero_locs = nonzero_locs[inds]
    msg = '    removed {} disconnected nodes'
    logger.debug(msg.format(num - nonzero_locs.size))
    #
    return nonzero_locs


def save_image_stack(nonzero_locs, img_dims, path, overwrite=False):
    r"""
    Saves a text image stack in a directory to be read by ImageJ
    """
    #
    logger.info('saving image data as .bmp stack...')
    #
    img_data = 255*sp.ones(img_dims, dtype=sp.uint8)
    x_coords, y_coords, z_coords = sp.unravel_index(nonzero_locs, img_dims)
    img_data[x_coords, y_coords, z_coords] = 0
    #
    # creating any needed directories
    try:
        os.makedirs(path)
    except FileExistsError:
        if not overwrite:
            msg = 'Image Stack destination already exists, '
            msg += ' use "-f" option to overwrite'
            raise FileExistsError(msg)
        else:
            files = glob(os.path.join(path, '*'))
            for f in files:
                os.remove(f)
    #
    # saving the image frames
    for frame in range(img_data.shape[2]):
        name = os.path.join(path, 'image-frame-{}.bmp'.format(frame))
        frame = Image.fromarray(img_data[:, :, frame].transpose())
        frame.save(name)


def generate_offset_map(nonzero_locs, shape):
    r"""
    Creates a map storing the index of the lowest y-axis pixel in an
    X-Z column.
    """
    #
    logger.info('creating initial offset map')
    #
    x_coords, y_coords, z_coords = sp.unravel_index(nonzero_locs, shape)
    data = sp.ones(shape, dtype=sp.uint16)*sp.iinfo(sp.int16).max
    data[x_coords, y_coords, z_coords] = y_coords
    #
    offset_map = sp.zeros((shape[0], shape[2]), dtype=sp.int16)
    for z_index in range(shape[2]):
        offset_map[:, z_index] = sp.amin(data[:, :, z_index], axis=1)
        offset_map[:, z_index][offset_map[:, z_index] > shape[1]] = -1
    #
    return offset_map


def patch_holes(data_map):
    r"""
    Fills in any areas with a value of -1 by taking a linear average of
    the nearest non-zero values along each axis
    """
    #
    logger.info('interpolating missing data due to zero aperture zones')
    #
    # getting coordinates of all valid data points
    data_vector = sp.ravel(data_map)
    inds = sp.where(data_vector >= 0)[0]
    points = sp.unravel_index(inds, data_map.shape)
    values = data_vector[inds]
    #
    # setting up to interpolate over all data coordinates
    intrp = sp.arange(data_map.size, dtype=int)
    intrp = sp.unravel_index(intrp, data_map.shape)
    #
    # interpolating data to fill gaps and creating the new data map
    data_vector = griddata(points, values, intrp, method='nearest')
    data_map = sp.reshape(data_vector, data_map.shape)
    #
    return data_map

#
if __name__ == '__main__':
    apm_calculate_offset_map()
