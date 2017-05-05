r"""
Description: Processes a binary tif stack, with the option to remove
disconnected voxels based on an undirected graph. The number of clusters
to retain can be specified and connectivity is defined on a 26 point basis,
i.e faces, edges and corners. Standard outputs include the processed
tif image stack, an aperture map and offset map based on the processed image.
Offset maps are filtered based on gradient steepness to provide a smoother
surface. Data gaps left by zero apeture zones or filtering are filled by
linear and nearest interpolation methods to prevent artificial features.

For usage information run: ``apm_process_image_stack -h``

| Written By: Matthew stadelman
| Date Written: 2016/08/30
| Last Modfied: 2017/04/23

|

"""
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
from itertools import product
import os
import scipy as sp
from scipy import sparse as sprs
from scipy.sparse import csgraph
from scipy.interpolate import griddata
from apmapflow import _get_logger, set_main_logger_level
from apmapflow import DataField, calc_percentile, FractureImageStack


# setting up logger
set_main_logger_level('info')
logger = _get_logger('apmapflow.scripts')

# creating arg parser
parser = argparse.ArgumentParser(description=__doc__, formatter_class=RawDesc)

# adding arguments
parser.add_argument('-f', '--force', action='store_true',
                    help='allows program to overwrite existing files')

parser.add_argument('-v', '--verbose', action='store_true',
                    help='debug messages are printed to the screen')

parser.add_argument('-o', '--output-dir',
                    type=os.path.realpath, default=os.getcwd(),
                    help='''outputs files to the specified
                    directory, sub-directories are created as needed''')

parser.add_argument('-n', '--num-clusters', type=int, default=None,
                    help='''number of clusters to retain, ordered by size
                    is option is disabled by default''')

parser.add_argument('-i', '--invert', action='store_true',
                    help='use this flag if your fracture is in black')

parser.add_argument('--offset-map-name', default=None,
                    help='alternate name to save the offset map as')

parser.add_argument('--aper-map-name', default=None,
                    help='alternate name to save the aperture map as')

parser.add_argument('--img-stack-name', default=None,
                    help='''alternate name to save the tiff stack as,
                    has no effect if the -n # flag is omitted''')

parser.add_argument('--gen-cluster-img', action='store_true',
                    help='generates a tiff image colored by cluster number')

parser.add_argument('--no-aper-map', action='store_true',
                    help='do not generate aperture map')

parser.add_argument('--no-offset-map', action='store_true',
                    help='do not generate offset map')

parser.add_argument('--no-img-stack', action='store_true',
                    help='''do not save a processed tif stack,
                    has no effect when the -n # flag is omitted''')

parser.add_argument('image_file', type=os.path.realpath,
                    help='binary TIFF stack image to process')


def main():
    r"""
    Driver program to load an image and generate maps. Memory
    requirements when processing a large TIFF stack can be very high.
    """
    # parsing commandline args
    args = parser.parse_args()
    if args.verbose:
        set_main_logger_level('debug')
    #
    # initializing output filenames as needed and pre-appending the output path
    img_basename = os.path.basename(args.image_file)
    img_basename = os.path.splitext(img_basename)[0]
    if args.aper_map_name is None:
        args.aper_map_name = img_basename + '-aperture-map.txt'
    #
    if args.offset_map_name is None:
        args.offset_map_name = img_basename + '-offset-map.txt'
    #
    if args.img_stack_name is None:
        args.img_stack_name = img_basename + '-processed.tif'
    #
    aper_map_file = os.path.join(args.output_dir, args.aper_map_name)
    offset_map_file = os.path.join(args.output_dir, args.offset_map_name)
    img_stack_file = os.path.join(args.output_dir, args.img_stack_name)
    #
    # checking paths
    if not args.no_aper_map:
        if os.path.exists(aper_map_file) and not args.force:
            msg = '{} already exists, use "-f" option to overwrite'
            raise FileExistsError(msg.format(aper_map_file))
    #
    if not args.no_offset_map:
        if os.path.exists(offset_map_file) and not args.force:
            msg = '{} already exists, use "-f" option to overwrite'
            raise FileExistsError(msg.format(offset_map_file))
    #
    if not args.no_img_stack:
        if os.path.exists(img_stack_file) and not args.force:
            msg = '{} already exists, use "-f" option to overwrite'
            raise FileExistsError(msg.format(img_stack_file))
    #
    # loading image data
    logger.info('loading image...')
    img_data = FractureImageStack(args.image_file)
    if args.invert:
        logger.debug('inverting image data')
        img_data = ~img_data
    logger.debug('image dimensions: {} {} {}'.format(*img_data.shape))
    #
    # processing image stack based on connectivity
    if args.num_clusters:
        kwargs = {
            'output_img': args.gen_cluster_img,
            'img_name': os.path.splitext(img_stack_file)[0] + '-clusters.tif',
            'img_shape': img_data.shape
        }
        img_data = process_image(img_data, args.num_clusters, **kwargs)

    #
    # outputing aperture map
    if not args.no_aper_map:
        aper_map = img_data.create_aperture_map()
        logger.info('saving aperture map file')
        sp.savetxt(aper_map_file, aper_map, fmt='%d', delimiter='\t')
        del aper_map
    #
    # outputing offset map
    if not args.no_offset_map:
        offset_map = calculate_offset_map(img_data)
        #
        # saving map
        logger.info('saving offset map file')
        sp.savetxt(offset_map_file, offset_map, fmt='%f', delimiter='\t')
        del offset_map
    #
    # saving image data
    if args.num_clusters and not args.no_img_stack:
        logger.info('saving copy of processed image data')
        img_data.save(img_stack_file, overwrite=args.force)


def process_image(img_data, num_clusters, **kwargs):
    r"""
    Processes a tiff stack on retaining voxels based on node connectivity.
    The clusters are sorted by size and the large N are retained.
    """
    #
    img_dims = img_data.shape
    nonzero_locs = img_data.get_fracture_voxels()
    index_map = generate_index_map(nonzero_locs, img_dims)
    #
    # determing connectivity and removing clusters
    conns = generate_node_connectivity_array(index_map, img_data)
    del img_data, index_map
    nonzero_locs = remove_isolated_clusters(conns,
                                            nonzero_locs,
                                            num_clusters,
                                            **kwargs)
    # reconstructing 3-D array
    logger.info('reconstructing processed data back into 3-D array')
    #
    img_data = sp.zeros(img_dims, dtype=bool)
    x_coords, y_coords, z_coords = sp.unravel_index(nonzero_locs, img_dims)
    #
    del nonzero_locs
    img_data[x_coords, y_coords, z_coords] = True
    del x_coords, y_coords, z_coords
    #
    return img_data.view(FractureImageStack)


def calculate_offset_map(img_data):
    r"""
    Handles calculation of an offset map based on image data
    """
    #
    logger.info('creating initial offset map')
    offset_map = img_data.create_offset_map(no_data_fill=sp.nan)
    #
    logger.info('interpolating missing data due to zero aperture zones')
    offset_map = patch_holes(offset_map)
    offset_map = filter_high_gradients(offset_map)
    #
    return offset_map


def generate_index_map(nonzero_locs, shape):
    r"""
    Determines the i,j,k indicies of the flattened array
    """
    #
    logger.info('creating index map of non-zero values...')
    x_c = sp.unravel_index(nonzero_locs, shape)[0].astype(sp.int16)
    y_c = sp.unravel_index(nonzero_locs, shape)[1].astype(sp.int16)
    z_c = sp.unravel_index(nonzero_locs, shape)[2].astype(sp.int16)
    index_map = sp.stack((x_c, y_c, z_c), axis=1)
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
    #
    conn_map = sp.array(conn_map, dtype=int)
    conn_map = conn_map[1:]
    #
    # creating slice list to process data chunks
    slice_list = [slice(0, 10000)]
    for i in range(slice_list[0].stop, index_map.shape[0], slice_list[0].stop):
        slice_list.append(slice(i, i+slice_list[0].stop))
    slice_list[-1] = slice(slice_list[-1].start, index_map.shape[0])
    #
    conns = sp.ones((0, 2), dtype=data_array.index_int_type)
    logger.debug('\tnumber of slices to process: {}'.format(len(slice_list)))
    percent = 10
    for n, sect in enumerate(slice_list):
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
        if int(n/len(slice_list)*100) == percent:
            logger.debug('\tprocessed slice {:5d}, {}% complete'.format(n, percent))
            percent += 10
    #
    # using scipy magic from stackoverflow to remove dupilcate connections
    logger.info('removing duplicate connections...')
    dim0 = conns.shape[0]
    conns = sp.ascontiguousarray(conns)
    dtype = sp.dtype((sp.void, conns.dtype.itemsize*conns.shape[1]))
    dim1 = conns.shape[1]
    conns = sp.unique(conns.view(dtype)).view(conns.dtype).reshape(-1, dim1)
    logger.debug('\tremoved {} duplicates'.format(dim0 - conns.shape[0]))
    #
    return conns


def generate_adjacency_matrix(conns, nonzero_locs):
    r"""
    generates a ajacency matrix based on connectivity array
    """
    msg = 're-indexing connections array from absolute to relative indicies'
    logger.info(msg)
    mapper = sp.ones(nonzero_locs[-1]+1, dtype=sp.uint32) * sp.iinfo(sp.uint32).max
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


def remove_isolated_clusters(conns, nonzero_locs, num_to_keep, **kwargs):
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
    del adj_mat, order
    num_to_keep = min(num_to_keep, groups.size)
    #
    msg = '\t{} component groups for {} total nodes'
    logger.debug(msg.format(groups.size, cs_ids.size))
    msg = '\tlargest group number: {}, size {}'
    logger.debug(msg.format(groups[0], counts[0]))
    msg = '\t{} % of nodes contained in largest group'
    logger.debug(msg.format(counts[0]/cs_ids.size*100))
    msg = '\t{} % of nodes contained in {} retained groups'
    num = sp.sum(counts[0:num_to_keep])/cs_ids.size*100
    logger.debug(msg.format(num, num_to_keep))
    #
    # creating image colored by clusters if desired
    if kwargs.get('output_img', False):
        save_cluster_image(cs_ids,
                           groups,
                           counts,
                           nonzero_locs,
                           kwargs.get('img_shape'),
                           kwargs.get('img_name'))
    #
    inds = sp.where(sp.in1d(cs_ids, groups[0:num_to_keep]))[0]
    del cs_ids, groups, counts
    #
    num = nonzero_locs.size
    nonzero_locs = nonzero_locs[inds]
    msg = '\tremoved {} disconnected nodes'
    logger.debug(msg.format(num - nonzero_locs.size))
    #
    return nonzero_locs


def save_cluster_image(cs_ids, groups, counts, locs, img_shape, img_name):
    r"""
    Saves an 8 bit image colored by cluster number
    """
    logger.info('creating tiff image file colored by cluster number')
    #
    msg = '\t{} % of nodes covered in {} colored groups'
    num_cs = min(16, groups.size)
    num = sp.sum(counts[0:num_cs])/cs_ids.size*100
    logger.debug(msg.format(num, num_cs))
    #
    # setting the top 16 groups separated by increments of 8 and the rest are 255
    data = sp.ones(cs_ids.size, dtype=sp.uint8) * 255
    for n, cs_id in enumerate(groups[0:num_cs-1]):
        inds = sp.where(cs_ids == cs_id)[0]
        data[inds] = 67 + n * 8
    #
    x_coords, y_coords, z_coords = sp.unravel_index(locs, img_shape)
    img_data = sp.zeros(img_shape, dtype=sp.uint8)
    img_data[x_coords, y_coords, z_coords] = data
    # save image data
    img_data = img_data.view(FractureImageStack)
    logger.info('saving image cluster data to file' + img_name)
    img_data.save(img_name, overwrite=True)


def patch_holes(data_map):
    r"""
    Fills in any areas with a non finite value by taking a linear average of
    the nearest non-zero values along each axis
    """
    #
    # getting coordinates of all valid data points
    data_vector = sp.ravel(data_map)
    inds = sp.where(sp.isfinite(data_vector))[0]
    points = sp.unravel_index(inds, data_map.shape)
    values = data_vector[inds]
    #
    # linearly interpolating data to fill gaps
    xi = sp.where(~sp.isfinite(data_vector))[0]
    msg = '\tattempting to fill %d values with a linear interpolation'
    logger.debug(msg, xi.size)
    xi = sp.unravel_index(xi, data_map.shape)
    intrp = griddata(points, values, xi, fill_value=sp.nan, method='linear')
    data_map[xi[0], xi[1]] = intrp
    #
    # performing a nearest interpolation any remaining regions
    data_vector = sp.ravel(data_map)
    xi = sp.where(~sp.isfinite(data_vector))[0]
    msg = '\tfilling %d remaining values with a nearest interpolation'
    logger.debug(msg, xi.size)
    xi = sp.unravel_index(xi, data_map.shape)
    intrp = griddata(points, values, xi, fill_value=0, method='nearest')
    data_map[xi[0], xi[1]] = intrp
    #
    return data_map


def filter_high_gradients(data_map):
    r"""
    Filters the offset field to reduce the number of very steep gradients.
    The magnitude of the gradient is taken and all values less than or
    greater than +-99th percentile are removed and recalculated.
    """
    #
    logger.info('filtering offset map to remove steeply sloped cells')
    #
    zdir_grad, xdir_grad = sp.gradient(data_map)
    mag = sp.sqrt(zdir_grad**2 + xdir_grad**2)
    data_map += 1
    data_vector = sp.ravel(data_map)
    #
    # setting regions outside of 99th percentile to 0 for cluster removal
    val = calc_percentile(99, sp.ravel(mag))
    data_map[zdir_grad < -val] = 0
    data_map[zdir_grad > val] = 0
    data_map[xdir_grad < -val] = 0
    data_map[xdir_grad > val] = 0
    #
    logger.debug('\tremoving clusters isolated by high gradients')
    offsets = DataField(data_map)
    adj_mat = offsets.create_adjacency_matrix()
    cs_num, cs_ids = csgraph.connected_components(csgraph=adj_mat,
                                                  directed=False)
    cs_num, counts = sp.unique(cs_ids, return_counts=True)
    cs_num = cs_num[sp.argsort(counts)][-1]
    #
    data_vector[sp.where(cs_ids != cs_num)[0]] = sp.nan
    data_map = sp.reshape(data_vector, data_map.shape)
    #
    # re-interpolating for the nan regions
    logger.debug('\tpatching holes left by cluster removal')
    patch_holes(data_map)
    #
    return data_map
