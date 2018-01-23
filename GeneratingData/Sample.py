from json import load
from pprint import pprint
from numpy import array
from argparse import ArgumentParser

def get_paths_from_command_line():
        parser = ArgumentParser()
        parser.add_argument("src")
        args = parser.parse_args()
        return args.src

def main():
        input_file = get_paths_from_command_line()
	with open(input_file, "r") as f:
		hands = load(f)
		hands = list(hands.values())
		print("North:")
		pprint(array(hands[0]["N"]))
		print("South:")
		pprint(array(hands[0]["S"]))
		print("IMPs:")
		pprint(array(hands[0]["IMP"]))

main()

