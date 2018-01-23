from json import load
from numpy import array, concatenate, vstack, save
from argparse import ArgumentParser

def get_paths_from_command_line():
        parser = ArgumentParser()
        parser.add_argument("src")
        parser.add_argument("dest")
        args = parser.parse_args()
        return args.src, args.dest

def main():
        input_file, output_file = get_paths_from_command_line()
        with open(input_file, "r") as f:
		hands = load(f).values()
		for hand in hands:
			hand["IMP"] = (array(hand["IMP"]) + 24.0) / 48.0
		hands = [[array(hand["N"]), array(hand["S"]), array(hand["IMP"])] for hand in hands]
		hands = [concatenate(hand, axis=0) for hand in hands]
		hands = vstack(hands)
		save(output_file, hands)

main()
