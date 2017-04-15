#!/usr/bin/env python3
r"""
Script designed to take a TIF stack and determine the fractal dimension
coefficent.
"""
import argparse
from argparse import RawDescriptionHelpFormatter as RawDesc
from collections import namedtuple
import os
import scipy as sp
from scipy import stats as sp_stats
from ApertureMapModelTools import _get_logger, set_main_logger_level
from ApertureMapModelTools import FractureImageStack

#
desc_str = r"""
Description: Reads in a tiff stack from the CT scanner and calculates the
fractal dimension (Df) along either the X and/or Z axis.

Written By: Matthew stadelman
Date Written: 2016/11/17
Last Modfied: 2017/02/12
"""
# setting up logger
set_main_logger_level('info')
logger = _get_logger('ApertureMapModelTools.Scripts')

# creating arg parser
parser = argparse.ArgumentParser(description=desc_str, formatter_class=RawDesc)

# adding arguments
parser.add_argument('-f', '--force', action='store_true',
                    help='allows program to overwrite existing files')

parser.add_argument('-v', '--verbose', action='store_true',
                    help='debug messages are printed to the screen')

parser.add_argument('-i', '--invert', action='store_true',
                    help='use this flag if your fracture is in black')

parser.add_argument('-o', '--output-dir',
                    type=os.path.realpath, default=os.getcwd(),
                    help='''outputs file to the specified
                    directory, sub-directories are created as needed''')

parser.add_argument('-x', '--x-axis', action='store_true',
                    help='calculates Df exponent along x axis')

parser.add_argument('-z', '--z-axis', action='store_true',
                    help='calculates Df exponent along z axis')

parser.add_argument('--bot', action='store_true',
                    help='calculates the bottom trace for the axes')

parser.add_argument('--mid', action='store_true',
                    help='calculates the middle trace for the axes (default)')

parser.add_argument('--top', action='store_true',
                    help='calculates the upper trace for the axes')

parser.add_argument('image_file', type=os.path.realpath,
                    help='binary TIF stack image to process')

parser.add_argument('data_filename', nargs='?', type=os.path.realpath,
                    help='name to save the data under')


class FractureSlice(object):
    r"""
    Stores the fractal information for a single slice
    """
    Fractal = namedtuple('fractal', ['dimension', 'num_points', 'r_squared'])

    def __init__(self, slice_data):
        r"""initialize the class"""
        super().__init__()
        #
        self._slice_data = sp.copy(slice_data)
        self.top = None
        self.bot = None
        self.mid = None
        self.aperture = None
        self.zero_ap_count = 0
        self.bifurcation_count = 0
        #
        self.fractals = {}

    @property
    def slice_data(self):
        r"""returns the slice data"""
        return self._slice_data

    @property
    def bifurcation_frac(self):
        r""" calculates fractional bifurcation """
        return self.bifurcation_count/self.slice_data.shape[0]

    @property
    def zero_ap_frac(self):
        r""" calculates fractional bifurcation """
        return self.zero_ap_count/self.slice_data.shape[0]

    def set_fractal(self, key, data):
        r"""
        Adds a named tuple containing fractal data to the fractals dict
        """
        fractal = self.Fractal(2 - data['slope'],
                               data['num_points'],
                               data['r_squared'])
        self.fractals[key] = fractal


def apm_fracture_df():
    r"""
    Driver program to load an image and process it to output hurst exponents
    """
    # parsing command line args
    args = parser.parse_args()
    if args.verbose:
        set_main_logger_level('debug')
    #
    # checking output file path and setting default if required
    if args.data_filename is None:
        args.data_filename = os.path.basename(args.image_file)
        args.data_filename = os.path.splitext(args.data_filename)[0]
        args.data_filename += '-df' + os.extsep + 'txt'
    args.data_filename = os.path.join(args.output_dir, args.data_filename)
    #
    if os.path.exists(args.data_filename) and not args.force:
        msg = 'File %s already exists, '
        msg += 'use "-f" option to overwrite'
        raise FileExistsError(msg % args.data_filename)
    #
    os.makedirs(os.path.split(args.data_filename)[0], exist_ok=True)
    #
    # setting up which traces to calculate
    if (args.bot or args.top) and not args.mid:
        traces = []
    else:
        traces = ['mid']
    #
    if args.bot:
        traces.append('bot')
    if args.top:
        traces.append('top')
    #
    # loading image data
    logger.info('loading image...')
    image_data = FractureImageStack(args.image_file)
    if args.invert:
        logger.debug('inverting image data')
        image_data = ~image_data
    logger.debug('image dimensions: {} {} {}'.format(*image_data.shape))
    #
    # processing data along each axis
    x_data = None
    if args.x_axis:
        logger.info('calculating the fractal dimension for the x-axis')
        x_data = []
        for i in range(0, image_data.shape[2]):
            logger.debug('Processing x axis slice %d', i)
            slice_data = image_data[:, :, i]
            fracture_slice = process_slice(slice_data, traces)
            x_data.append(fracture_slice)
    #
    z_data = None
    if args.z_axis:
        logger.info('calculating the fractal dimension for the z-axis')
        z_data = []
        for i in range(image_data.shape[0]):
            logger.debug('Processing z axis slice %d', i)
            slice_data = image_data[i, :, :].T
            fracture_slice = process_slice(slice_data, traces)
            z_data.append(fracture_slice)

    # saving data
    logger.info('saving fractal dimension exponent data to file')
    with open(args.data_filename, 'w') as outfile:
        output_data(outfile, traces, x_data=x_data, z_data=z_data)


def process_slice(slice_data, traces):
    r"""
    Processes slice data to measure the changes
    in the trace height along the fracture, using the variable bandwidth
    method, then find the best fit linear line to calculate the Hurst exponent.
    """
    fracture_slice = FractureSlice(slice_data)
    #
    # processing data to get profile traces
    logger.debug('\tdetermining fracture slice line traces')
    find_profiles(fracture_slice)
    #
    # calculating fractals for each trace
    for trace in traces:
        logger.debug('\tcalculating bandwidth std-dev for %s trace', trace)
        std_dev_bands = calculate_df(fracture_slice.__getattribute__(trace))
        logger.debug('\tregression fitting to get Df for %s trace', trace)
        minimum = df_best_fit(std_dev_bands)
        fracture_slice.set_fractal(trace, minimum)
    #
    return fracture_slice


def find_profiles(fracture_slice):
    r"""
    Takes in a 2-D data slice and generates line traces for JRC and Df
    analysis.

    Returns a dictionary of the top, bottom and midsurface traces as well
    as the fraction of bifurcations and zero aperture zones.
    """
    #
    data = fracture_slice.slice_data
    #
    aperture = sp.sum(data, axis=1, dtype=int)
    non_zero = sp.where(data.ravel() > 0)[0]
    a1_coords, a2_coords = sp.unravel_index(non_zero, data.shape)
    #
    # getting the three profiles
    profile = sp.ones(data.shape, dtype=float) * sp.inf
    profile[a1_coords, a2_coords] = a2_coords
    bottom = sp.amin(profile, axis=1)
    bottom[~sp.isfinite(bottom)] = sp.nan
    #
    profile = sp.ones(data.shape, dtype=float) * -sp.inf
    profile[a1_coords, a2_coords] = a2_coords
    top = sp.amax(profile, axis=1)
    top[~sp.isfinite(top)] = sp.nan
    #
    mid = (bottom + top)/2.0
    #
    # calcualting bifurcation locations
    bif_frac = top - bottom + 1  # because I store both fracture voxel indices
    bif_frac[aperture == 0] = 0  # zero aperture zones are excluded
    bif_frac = bif_frac.astype(int)
    #
    # updating attributes
    fracture_slice.top = top
    fracture_slice.bot = bottom
    fracture_slice.mid = mid
    fracture_slice.aperture = aperture
    fracture_slice.zero_ap_count = sp.where(aperture == 0)[0].size
    fracture_slice.bifurcation_count = sp.where(bif_frac != aperture)[0].size


def calculate_df(line_trace):
    r"""
    Code initially written by Charles Alexander in 2013
    Modified by Dustin Crandall in 2015
    Rewritten into Python by Matt Stadelman 11/15/2016

    Based on the methodology presented in Dougan, Addison & McKenzie's
    2000 paper "Fractal Analysis of Fracture: A Comparison of Methods" in
    Mechanics Research Communications.

    The Hurst exponent is defined as equal to 2 - the fractal dimension of
    a fracture profile

    H = 2 - Df
    Df = 2 - H

    The method calculates the Hurst Exponent of a fracture profile using the
    "Variable Bandwidth Method", wherein a window of size 's' is moved along
    the fracture profile and the standard deviation of the displacement of the
    profile at the ends of the window is calculated

                       N-s
    sigma_s = [(1/N-s)*SUM((Profile_height(i) - Profile_height(i+s))^2)]^1/2
                       i=1

    where sigma_s = incremental standard deviation
    N = number of data points
    Profile_height(x) = height of profile at x

    H is determined as the slope of the plot of log10(sigma_s) against log10(s)

    returns a range of standard deviations for each bandwidth useds
    """
    #
    # setting through a range of bandwidths
    std_devs = []
    line_trace = sp.copy(line_trace)
    for bandwidth in sp.arange(4, line_trace.size/3, dtype=int):
        # initialing varaibles
        npts = line_trace.size - bandwidth - 1
        #
        start = line_trace[0:npts]
        end = line_trace[bandwidth:-1]
        #
        sqr_diff = (end - start)**2
        sqr_diff[~sp.isfinite(sqr_diff)] = 0
        #
        std_dev = (sp.sum(sqr_diff) / npts)**0.5
        std_dev = std_dev if std_dev != 0 else 1.5
        #
        std_devs.append([bandwidth, std_dev])
    #
    return sp.array(std_devs, ndmin=2)


def df_best_fit(df_data):
    r"""

    With large window sizes the realtionship between the log10(window size) and
    the log10(standard deviation of change in height) does not appear to follow
    a linear trend, which we should see to calculate the Hurst Exponent

    This function is designed to find where the R^2 value of a linear fit to
    the data is minimum
    """
    #
    # setting up vectors
    log_band = sp.log(df_data[:, 0])
    log_std_dev = sp.log(df_data[:, 1])
    #
    # calculating linear regressions
    min_r2 = 1.0
    min_data = None
    for fit_size in sp.arange(log_band.size/4, log_band.size, dtype=int):
        #
        x_vals = log_band[0:fit_size]
        y_vals = log_std_dev[0:fit_size]
        m, b, r_val = sp_stats.linregress(x_vals, y_vals)[0:3]
        #
        data = {
            'num_points': fit_size,
            'slope': m,
            'y_int': b,
            'r_squared': r_val**2
        }
        #
        if r_val**2 < min_r2:
            min_r2 = r_val**2
            min_data = data
    #
    return min_data


def output_data(file_handle, traces, x_data=None, z_data=None):
    r"""
    generates a tab delimited text file to store all of the data
    """
    #
    fmt = '{0:7d}'
    header = '%s'
    for trace in traces:
        header += '  [Trace\tDf      \tR^2      \tnpts]'
        fmt += '  %s\t{%s.dimension:0.6f}' % (trace, trace)
        fmt += '\t{%s.r_squared:0.6f}' % trace
        fmt += '\t{%s.num_points:4d}' % trace
    header += '\n'
    fmt += '\n'
    #
    if x_data is not None:
        file_handle.write('Df data along X-axis\n')
        file_handle.write(header % 'Z Index')
        #
        for i, frac_slice in enumerate(x_data):
            file_handle.write(fmt.format(i, **frac_slice.fractals))
    #
    if x_data and z_data:
        file_handle.write('\n')
    #
    if z_data is not None:
        file_handle.write('Df data along Z-axis\n')
        file_handle.write(header % 'X Index')
        #
        for i, frac_slice in enumerate(z_data):
            file_handle.write(fmt.format(i, **frac_slice.fractals))


if __name__ == '__main__':
    apm_fracture_df()
