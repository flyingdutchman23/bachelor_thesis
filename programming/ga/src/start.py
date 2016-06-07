import argparse

import config

import simple_ga

parser = argparse.ArgumentParser(
    description='Start the genetic algorithm with the given config file.')
parser.add_argument('configfile', metavar='C', type=str,
                            help='the path to the config file')

def main():
    args = parser.parse_args()
    config.fill_config(args.configfile)
    simple_ga.init()
    print("after init")
    simple_ga.run()

    
if __name__ == "__main__":
    main()
