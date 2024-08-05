"""
A driver for creating an ml input for a 253 feature prr model.
The input is 250 line segment samples, the log-distance,
the log of the absolute altitude difference, and a constant
"""
import numpy as np
import statsmodels.api as sm
import geopandas as gpd
from shapely.geometry import Point

class ML253FeaturesInput():
    """
    A class for generating ml model inputs using the 253 feature model.
    The input contains 250 line of sight samples, the log-distance, 
    the log of the absolute altitude difference, and a constant
    """
    def __init__(self, dems, facs, sampler, ncols=250):
        """
        Create a new input generator

        :param dems: a GeoDataFrame of the demand points to compute inputs to

        :param facs: a GeoDataFrame of the facility points to compute inputs from

        :param sampler: an instance of geo.sampler instantiated with dems and facs
        """
        self._dems = dems
        self._facs = facs
        self._sampler = sampler
        self._ncols = ncols
        self._all_dems = np.full(len(dems), True)

    def _generate_sample_points(self, fac, dems=None):
        # Returns the locations to sample, the shape to reshape to after sampling, and altitudes
        if dems is None:
            dems = self._all_dems

        fac_start = False # When true the line segment originates from the facility, usually false
        if fac_start:
            fs, ds = (0, 1)
        else:
            fs, ds = (1, 0)
        
        segments = np.empty((dems.sum(), 2, 2))
        segments[:, fs, 0] = self._facs.geometry[fac].x
        segments[:, fs, 1] = self._facs.geometry[fac].y
        segments[:, ds, 0] = self._dems.geometry.x[dems]
        segments[:, ds, 1] = self._dems.geometry.y[dems]

        altitudes = np.empty((dems.sum(), 2))
        altitudes[:, fs] = self._facs['altitude'][fac]
        altitudes[:, ds] = self._dems['altitude'][dems]
        
        segments = np.linspace(segments[:, 0, :], segments[:, 1, :], self._ncols, axis=1)
        altitudes = np.linspace(altitudes[:, 0], altitudes[:, 1], self._ncols, axis=1)

        seg_shape = segments.shape
        return (segments.reshape((seg_shape[0] * seg_shape[1], seg_shape[2])), [seg_shape, altitudes])
    
    def _reshape_samples(self, arr, seg_shape, altitudes):
        # Reshape the samples back after sampling
        arr = arr.reshape(seg_shape[:2])
        return (altitudes - arr)

    def get_input(self, fac, dems=None):
        """
        Get the input from fac to dems, includes the constant

        :param fac: the facility to get input from

        :param dems: a boolean numpy array of the demand points to get. 
        Will get the inputs to each demand point where dems[i] is True.
        If None is passed in then it will get the input to all demand points

        :returns: A dems.sum() x 253 numpy array of inputs if demands is not None 
        """
        if dems is None:
            dems = self._all_dems
        distances = np.log(0.01 + self._dems[dems].distance(self._facs.geometry[fac]).to_numpy())
        heights = np.log(0.01 + np.absolute(self._dems['altitude'][dems] - self._facs['altitude'][fac]))

        samples, args = self._generate_sample_points(fac, dems)
        samples = self._sampler.batched_sample(samples[:, 0], samples[:, 1])
        los = self._reshape_samples(samples, *args)

        X = np.empty((los.shape[0], los.shape[1] + 2))
        X[:, :-2] = los
        X[:, -2] = distances
        X[:, -1] = heights

        return sm.add_constant(X, has_constant='add')

def make_traindata(link_file, sampler, x_out, y_out, crs=None, logging=False):
    """
    Create and save training data for a given training dataset

    :param link_file: a path to a GeoDataFrame containing the data.
    The geometry should be 2-point Shapely linestrings where 
    the first point of each linestring is the transmission 
    location and the second point of each linestring is the 
    receiver location. There should be an 'ele_tr' field giving
    the altitude of the transmission and an 'ele_gw' field with
    the altitude of the receiver. There should be a 'success'
    field that is an '0' if the transmission failed and a '1'
    if the transmission succeeded.

    :param sampler: a geo.sampler instance with the same units
    of altitude as ele_tr and ele_gw

    :param x_out: the path to put the training inputs. The file
    should be a '.npy' file, and this extension will be appended
    if it is not present

    :param y_out: the path to put the training outputs. The file
    should be a '.npy' file, and this extension will be appended
    if it is not present

    :param crs: a coordinate reference system to use, should be
    a utm. Defaults to None, which means to use the link_file's crs.
    To find a utm, look into GeoDataFrame.estimate_utm_crs

    :param logging: boolean representing if progress should be 
    printed defaults to False
    """
    def ends_in(s, ending):
        return s[-1*len(ending):] == ending

    x_out += (not ends_in(x_out, ".npy")) * ".npy"
    y_out += (not ends_in(y_out, ".npy")) * ".npy"

    links = gpd.read_file(link_file)
    if crs is None:
        crs = links.crs
    links = links.to_crs(crs)

    first_pt = lambda line: Point(line.coords[0])
    second_pt = lambda line: Point(line.coords[1])

    dems = gpd.GeoDataFrame(geometry=gpd.GeoSeries([first_pt(i) for i in links.geometry]), crs=crs)
    dems['altitude'] = links['ele_tr']
    facs = gpd.GeoDataFrame(geometry=gpd.GeoSeries([second_pt(i) for i in links.geometry]), crs=crs)
    facs['altitude'] = links['ele_gw']

    X = np.empty((len(links), 253))
    y = np.array([int(i) for i in links['success']])

    input_gen = ML253FeaturesInput(dems, facs, sampler)

    for i in range(len(links)):
        if logging:
            print(f"{i+1} / {len(links)}", end="\r")
        dem_choice = np.full(len(dems), False)
        dem_choice[i] = True
        X[i] = input_gen.get_input(i, dem_choice)[0]
    
    finite_mask = np.isfinite(X)
    finite_rows = np.all(finite_mask, axis=1)
    X = X[finite_rows]
    y = y[finite_rows]

    np.save(x_out, X)
    np.save(y_out, y)
