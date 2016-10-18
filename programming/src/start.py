import argparse

import config

import simple_ga

parser = argparse.ArgumentParser(
    description='Start the genetic algorithm with the given config file.')
parser.add_argument('configfile', metavar='C', type=str,
                            help='the path to the config file')
parser.add_argument('--show', dest='show', action='store_true',
                            help='shows the result at end')
parser.add_argument('--no-show', dest='show', action='store_false',
                            help='does not show the result at end')
parser.set_defaults(show=True)

def main():
    args = parser.parse_args()
    config.fill_config(args.configfile)
    simple_ga.init()
    print("after init!!!")
    print()
    simple_ga.run(show=args.show)

    
if __name__ == "__main__":
    main()
