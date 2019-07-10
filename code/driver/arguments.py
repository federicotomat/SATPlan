import argparse
import os


DESCRIPTION = """Planner driver script."""

def is_valid_file(arg):
    if not os.path.exists(arg):
        raise argparse.ArgumentTypeError('{} not found!'.format(arg))
    elif not os.path.splitext(arg)[1] == ".pddl":
        raise argparse.ArgumentTypeError('{} is not a valid PDDL file!'.format(arg))
    else:
        return arg


def parse_args():
    parser = argparse.ArgumentParser(description = DESCRIPTION)

    parser.add_argument('problem', metavar='problem.pddl', help='Path to PDDL problem file', type=is_valid_file)

    ########################
    ## Optional arguments ##
    ########################

    parser.add_argument('-domain', help='Path to PDDL domain file', type=is_valid_file)

    parser.add_argument('-linear', action='store_true', help='Builds a sequential encoding.')

    parser.add_argument('-parallel', action='store_true', help='Builds a parallel encoding.')

    parser.add_argument('-pprint', action='store_true', help='Prints the plan to file (when one can be found).')

    args = parser.parse_args()

    return args
