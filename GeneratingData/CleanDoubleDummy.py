from boltons import iterutils
from math import log
from multiprocessing import Pool
from json import dump
from argparse import ArgumentParser

def parse_card(card):
	card = card.split()
	suite = int(card[0])
	rank = int(card[1])
	rank = int(log(rank, 2))
	return (suite, rank)

def parse_hand(hand):
	hand = [pos[:-1].split("\t") for pos in hand]
	hand = [[parse_card(card) for card in pos] for pos in hand]
	return hand

def parse_tricks(tricks):
	tricks = [trick.split(" ") for trick in tricks]
	tricks = [(int(trick[0]), int(trick[1])) for trick in tricks]
	return tricks

def jsonify_data_point(line):
	json_game = {}
	game = line[0]
	json_game["N"] = game[0][0]
	json_game["S"] = game[0][1]
	json_game["MaxTricks"] = [game[1] for game in line]
	return json_game

def transform_line(line):
	line = [game[:-1] for game in line[:-1]]
	line = iterutils.chunked(line, 9)
	line = [[parse_hand(game[:4]), parse_tricks(game[4:])] for game in line]
	line = jsonify_data_point(line)
	return line

def get_paths_from_command_line():
	parser = ArgumentParser()
	parser.add_argument("src")
	parser.add_argument("dest")
	args = parser.parse_args()
	return args.src, args.dest

def main():
	input_file, output_file = get_paths_from_command_line()
	line = {}
	with open(input_file,"r") as f:
		lines = iterutils.chunked(f.readlines(), 46)
		pool = Pool()
		lines = list(pool.map(transform_line, lines))
		pool.close()
	with open(output_file,"w") as f:
		lines = {idx:line for idx, line in enumerate(lines)}
		dump(lines, f, indent=4)

main()
