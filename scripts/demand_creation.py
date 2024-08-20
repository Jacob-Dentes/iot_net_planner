from make_pypath import pathify
pathify() 
import sys

from iot_net_planner.geo.demand_grid import generate_grid_with_points, load_file
from iot_net_planner.geo.dsm_sampler import DSMSampler

def main(dsm_file, area_file, output_path, points):
    utm = load_file(area_file).estimate_utm_crs()
    with DSMSampler(utm, dsm_file, 0) as sampler:
        demands = generate_grid_with_points(area_file, points, sampler, utm)
    demands.to_file(output_path)

if __name__ == "__main__":
    args = list(sys.argv[1:])
    
    main(args[0], args[1], args[2], int(args[3]))
    
