from iot_net_planner.geo.simplex_sampler import SimplexSampler
from iot_net_planner.optimization.bnp_model import BNPModel
from iot_net_planner.optimization.scip_model import SCIPModel

from iot_net_planner.prediction.prr_cache import CachedPRRModel
from iot_net_planner.prediction.ml_models.los_model_3features import LOS3Features

import geopandas as gpd
import numpy as np
import pickle as pkl
from importlib.resources import files
from os import environ
from onnxruntime import InferenceSession

seed = 100
np.random.seed(seed)
ncols = 150
nyc_crs = "epsg:2263"
model_file = files("iot_net_planner").joinpath("prediction/ml_models/3features_ithaca_LR_april3_prr.pth")

# File available at https://cornell.box.com/s/gihu98kc2o6l53oue9qfktvzmiy6jap5 named brooklyn_gateways.geojson
# Do not forget to set the environment variable:
# On Mac/Linux: https://askubuntu.com/questions/58814/how-do-i-add-environment-variables#58828
# On Windows: https://www.howtogeek.com/787217/how-to-edit-environment-variables-on-windows-10-or-11/
fac_file = environ['BROOKLYN_FAC']
# File available at https://cornell.box.com/s/gihu98kc2o6l53oue9qfktvzmiy6jap5 named brooklyn_demands.geojson
dem_file = environ['BROOKLYN_DEM']
sc_file = files("iot_net_planner").joinpath("prediction/ml_models/brooklyn_sc_3.onnx")

with open(sc_file, "rb") as f:
    onx = f.read()
standard_scalar = InferenceSession(onx)

sampler = SimplexSampler(seed)

facs = gpd.read_file(fac_file).to_crs(nyc_crs)
dems = gpd.read_file(dem_file).to_crs(nyc_crs)

facs['cost'] = np.ones(len(facs))
facs['built'] = np.zeros(len(facs))
facs['altitude'] = np.array([sampler.sample(x, y) for x, y in zip(facs.geometry.x, facs.geometry.y)])
facs['altitude'] += np.random.uniform(0.0, facs['altitude'].max(), len(facs))
dems['altitude'] = np.array([sampler.sample(x, y) for x, y in zip(dems.geometry.x, dems.geometry.y)])

prr = CachedPRRModel(LOS3Features(dems, facs, sampler, model_file, standard_scalar))

print(f"Loaded instance with {len(facs)} potential gateways and {len(dems)} demand points.")

print("Running BNP...")
print(BNPModel.solve_coverage(40.0, 0.1, dems, facs, prr, logging=False))

print("Running regular with cached model...")
print(SCIPModel.solve_coverage(40.0, 0.1, dems, facs, prr, logging=False))
