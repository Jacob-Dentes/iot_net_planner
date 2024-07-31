import geopandas as gpd
import numpy as np
import pickle as pkl
from importlib.resources import files
from os import environ
from onnxruntime import InferenceSession

from iot_net_planner.optimization.bnp_model import BNPModel

from iot_net_planner.prediction.prr_cache import CachedPRRModel
from iot_net_planner.prediction.ml_models.los_model_3features import LOS3Features
from iot_net_planner.geo.dsm_sampler import DSMSampler

# File available at https://cornell.box.com/s/gihu98kc2o6l53oue9qfktvzmiy6jap5 named geneva-dsm.tif
# Do not forget to set the environment variable
# On Mac/Linux: https://askubuntu.com/questions/58814/how-do-i-add-environment-variables#58828
# On Windows: https://www.howtogeek.com/787217/how-to-edit-environment-variables-on-windows-10-or-11/
dsm_file = environ['GENEVA_DSM']
# File available at https://cornell.box.com/s/gihu98kc2o6l53oue9qfktvzmiy6jap5 named geneva_gateways.geojson
# Do not forget to set the environment variable as above
fac_file = environ['GENEVA_FAC']
# File available at https://cornell.box.com/s/gihu98kc2o6l53oue9qfktvzmiy6jap5 named geneva_demands.geojson
# Do not forget to set the environment variable as above
dem_file = environ['GENEVA_DEM']

utm = "EPSG:32618"

model_file = files("iot_net_planner").joinpath("prediction/ml_models/3features_ithaca_LR_april3_prr.pth")
sc_file = files("iot_net_planner").joinpath("prediction/ml_models/brooklyn_sc_3.onnx")

with open(sc_file, "rb") as f:
    onx = f.read()
standard_scalar = InferenceSession(onx)

facs = gpd.read_file(fac_file).to_crs(utm)
dems = gpd.read_file(dem_file).to_crs(utm)

facs['cost'] = np.ones(len(facs))
facs['built'] = np.zeros(len(facs))

with DSMSampler(dems.crs, dsm_file) as sampler:
    prr = CachedPRRModel(LOS3Features(dems, facs, sampler, model_file, standard_scalar))

    print(f"Loaded instance with {len(facs)} potential gateways and {len(dems)} demand points.")

    print("Running BNP...")
    print(BNPModel.solve_coverage(5.0, 0.1, dems, facs, prr, qinc=0.8, logging=True))

