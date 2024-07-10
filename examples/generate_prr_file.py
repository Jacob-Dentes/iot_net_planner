from iot_net_planner.geo.simplex_sampler import SimplexSampler
from iot_net_planner.optimization.bnp_model import BNPModel
from iot_net_planner.optimization.scip_model import SCIPModel

from iot_net_planner.prediction.prr_cache import CachedPRRModel
from iot_net_planner.prediction.ml_models.los_model_3features import LOS3Features

import geopandas as gpd
import numpy as np
import pickle as pkl
from importlib.resources import files

seed = 100
np.random.seed(seed)
ncols = 150
nyc_crs = "epsg:2263"
model_file = files("iot_net_planner").joinpath("prediction/ml_models/3features_ithaca_LR_april3_prr.pth")

fac_file = "/Users/jacobdentes/IoT/network-planner-streamlined/nyc/nyc_gateways.geojson"
dem_file = "/Users/jacobdentes/IoT/network-planner-2024/data/brooklyn_demands_full_outdoor.geojson"
sc_file = files("iot_net_planner").joinpath("prediction/ml_models/brooklyn_sc_3.pkl")

with open(sc_file, "rb") as f:
    standard_scalar = pkl.load(f)
print(standard_scalar)

sampler = SimplexSampler(seed)

facs = gpd.read_file(fac_file).to_crs(nyc_crs)
dems = gpd.read_file(dem_file).to_crs(nyc_crs)

facs['cost'] = np.ones(len(facs))
facs['built'] = np.zeros(len(facs))
facs['altitude'] = np.array([sampler.sample(x, y) for x, y in zip(facs.geometry.x, facs.geometry.y)])
facs['altitude'] += np.random.uniform(0.0, facs['altitude'].max(), len(facs))
dems['altitude'] = np.array([sampler.sample(x, y) for x, y in zip(dems.geometry.x, dems.geometry.y)])

prr = CachedPRRModel(LOS3Features(dems, facs, sampler, model_file, standard_scalar))

prr.save_prrs("/Users/jacobdentes/IoT/brooklyn_simplex_prrs.npy")
