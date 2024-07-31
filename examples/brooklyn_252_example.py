from iot_net_planner.geo.simplex_sampler import SimplexSampler

from iot_net_planner.prediction.prr_cache import CachedPRRModel
from iot_net_planner.prediction.xg_253features import XG253Features

from iot_net_planner.geo.plotting import plot_fac_coverage

import geopandas as gpd
import numpy as np
import pickle as pkl
from importlib.resources import files
from os import environ
from onnxruntime import InferenceSession


seed = 100
np.random.seed(seed)
nyc_crs = "epsg:2263"
model_file = files("iot_net_planner").joinpath("prediction/ml_models/brooklyn_xgboost_combined_250x1_with_d_h.json")

# File available at https://cornell.box.com/s/gihu98kc2o6l53oue9qfktvzmiy6jap5 named brooklyn_gateways.geojson
# Do not forget to set the environment variable:
# On Mac/Linux: https://askubuntu.com/questions/58814/how-do-i-add-environment-variables#58828
# On Windows: https://www.howtogeek.com/787217/how-to-edit-environment-variables-on-windows-10-or-11/
fac_file = environ['BROOKLYN_FAC']
# File available at https://cornell.box.com/s/gihu98kc2o6l53oue9qfktvzmiy6jap5 named brooklyn_demands.geojson
dem_file = environ['BROOKLYN_DEM']
sc_file = files("iot_net_planner").joinpath("prediction/ml_models/brooklyn_scaler_model.onnx")


with open(sc_file, "rb") as f:
    onx = f.read()
standard_scalar = InferenceSession(onx)

sampler = SimplexSampler(seed, 0.1)

facs = gpd.read_file(fac_file).to_crs(nyc_crs)
dems = gpd.read_file(dem_file).to_crs(nyc_crs)

facs['cost'] = np.ones(len(facs))
facs['built'] = np.zeros(len(facs))
facs['altitude'] = np.array([sampler.sample(x, y) for x, y in zip(facs.geometry.x, facs.geometry.y)])
facs['altitude'] += np.random.uniform(0.0, facs['altitude'].max(), len(facs))
dems['altitude'] = np.array([sampler.sample(x, y) for x, y in zip(dems.geometry.x, dems.geometry.y)])

prr = CachedPRRModel(XG253Features(dems, facs, sampler, model_file, standard_scalar))

print(f"Loaded instance with {len(facs)} potential gateways and {len(dems)} demand points.")
to_0 = prr.get_prr(0)
print(to_0)
print(to_0.min())
print(to_0.max())
print(to_0.mean())
plot_fac_coverage(dems, facs, 0, to_0)

# print("Running BNP...")
# print(BNPModel.solve_coverage(40.0, 0.1, dems, facs, prr, logging=False))

# print("Running regular with cached model...")
# print(SCIPModel.solve_coverage(40.0, 0.1, dems, facs, prr, logging=False))
