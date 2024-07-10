import geopandas as gpd
import numpy as np
import pickle as pkl
from importlib.resources import files

from iot_net_planner.optimization.bnp_model import BNPModel

from iot_net_planner.prediction.prr_cache import CachedPRRModel
from iot_net_planner.prediction.ml_models.los_model_3features import LOS3Features
from iot_net_planner.geo.dsm_sampler import DSMSampler

dsm_file = "/Users/jacobdentes/IoT/network-planner-2024/geneva/geneva-dsm.tif"
fac_file = "/Users/jacobdentes/IoT/network-planner-2024/geneva/geneva_facilities.geojson"
dem_file = "/Users/jacobdentes/IoT/network-planner-2024/geneva/geneva_demands.geojson"

utm = "EPSG:32618"

model_file = files("iot_net_planner").joinpath("prediction/ml_models/3features_ithaca_LR_april3_prr.pth")
sc_file = files("iot_net_planner").joinpath("prediction/ml_models/brooklyn_sc_3.pkl")

with open(sc_file, "rb") as f:
    standard_scalar = pkl.load(f)

facs = gpd.read_file(fac_file).to_crs(utm)
dems = gpd.read_file(dem_file).to_crs(utm)

facs['cost'] = np.ones(len(facs))
facs['built'] = np.zeros(len(facs))

sampler = DSMSampler(dems, facs, dsm_file)
prr = CachedPRRModel(LOS3Features(dems, facs, sampler, model_file, standard_scalar))

print(f"Loaded instance with {len(facs)} potential gateways and {len(dems)} demand points.")

print("Running BNP...")
print(BNPModel.solve_coverage(5.0, 0.1, dems, facs, prr, qinc=0.8, logging=True))

sampler.clean_up()
