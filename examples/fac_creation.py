from make_pypath import pathify
pathify() 
import sys

from iot_net_planner.geo.demand_grid import load_file
from iot_net_planner.geo.estimate_facs import generate_facs
from iot_net_planner.geo.dsm_sampler import DSMSampler

def main(dsm_file, area_file, output_path, n_facs):
    area = load_file(area_file)
    utm = area.estimate_utm_crs()
    area = area.to_crs(utm)
    with DSMSampler(utm, dsm_file, 0) as sampler:
        demands = generate_facs(area, n_facs, sampler)
    demands.to_file(output_path)
    if n_facs is None:
        print(f"Generated {len(demands)} potential gateways.")

if __name__ == "__main__":
    args = list(sys.argv[1:])
    
    if len(args) == 4:
        main(args[0], args[1], args[2], int(args[3]))
    elif len(args) == 3:
        main(args[0], args[1], args[2], None)
