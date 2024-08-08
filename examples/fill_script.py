from iot_net_planner.geo.dsm_filler import fill_file
import sys

def main(original, new, band=1):
    fill_file(original, new, band)

def __main__():
    args = list(sys.argv[1:])

    if len(args) == 3:
        main(args[0], args[1], int(args[2]))
    elif len(args) == 2:
        main(args[0], args[1])
    else:
        print("Incorrect number of arguments. Expected old_dsm new_dsm")
    
