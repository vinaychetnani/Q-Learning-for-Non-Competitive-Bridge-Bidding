from json import load, dump
from multiprocessing import Pool
from argparse import ArgumentParser
from numpy import zeros, round

def score(input_tuple):
	bid_tricks, trump, max_tricks = input_tuple
	declarer_score = 0
	defender_score = 0

	# Major suit trump.
	if trump == 0 or trump == 1:

		# Did the declarer make at least 6 tricks?
		if max_tricks > 6:
			contract_tricks = min(max_tricks-6, bid_tricks)
			declarer_score += 30 * contract_tricks

		# Were there overtricks?
		if max_tricks > (bid_tricks+6):
			over_tricks = max_tricks - bid_tricks - 6
			declarer_score += 30 * over_tricks

	# Minor suit trump.
	elif trump == 2 or trump == 3:

		# Did the declarer make at least 6 tricks?
		if max_tricks > 6:
			contract_tricks = min(max_tricks-6, bid_tricks)
			declarer_score += 20 * contract_tricks

		# Were there overtricks?
		if max_tricks > (bid_tricks+6):
			over_tricks = max_tricks - bid_tricks - 6
			declarer_score += 20 * over_tricks

	# No trump.
	else:

		# Did the declarer make at least 6 tricks?
		if max_tricks > 6:
			contract_tricks = min(max_tricks-6, bid_tricks)
			declarer_score += 30 * contract_tricks
			declarer_score += 10

		# Were there overtricks?
		if max_tricks > (bid_tricks+6):
			over_tricks = max_tricks - bid_tricks - 6
			declarer_score += 30 * over_tricks

	# Were there penalty points?
	if max_tricks < (bid_tricks+6):
		under_tricks = bid_tricks + 6 - max_tricks
		defender_score += 50 * under_tricks

	# Was there a slam?
	if max_tricks == 12:
		declarer_score += 500
	elif max_tricks == 13:
		declarer_score += 1000

	# Converting to IMP
	diff = abs(declarer_score - defender_score)
	imp = 0
	if diff >= 20 and diff < 50:
		imp = 1
	elif diff >= 50 and diff < 90:
		imp = 2
	elif diff >= 90 and diff < 130:
		imp = 3
	elif diff >= 130 and diff < 170:
		imp = 4
	elif diff >= 170 and diff < 220:
		imp = 5
	elif diff >= 220 and diff < 270:
		imp = 6
	elif diff >= 270 and diff < 320:
		imp = 7
	elif diff >= 320 and diff < 370:
		imp = 8
	elif diff >= 370 and diff < 430:
		imp = 9
	elif diff >= 430 and diff < 500:
		imp = 10
	elif diff >= 500 and diff < 600:
		imp = 11
	elif diff >= 600 and diff < 750:
		imp = 12
	elif diff >= 750 and diff < 900:
		imp = 13
	elif diff >= 900 and diff < 1100:
		imp = 14
	elif diff >= 1100 and diff < 1300:
		imp = 15
	elif diff >= 1300 and diff < 1500:
		imp = 16
	elif diff >= 1500 and diff < 1750:
		imp = 17
	elif diff >= 1750 and diff < 2000:
		imp = 18
	elif diff >= 2000 and diff < 2250:
		imp = 19
	elif diff >= 2250 and diff < 2500:
		imp = 20
	elif diff >= 2500 and diff < 3000:
		imp = 21
	elif diff >= 3000 and diff < 3500:
		imp = 22
	elif diff >= 3500 and diff < 4000:
		imp = 23
	elif diff >= 4000:
		imp = 24

	if declarer_score > defender_score:
		return imp
	else:
		return (-1) * imp 

def precompute_scores():
	input_space = [(bid_tricks, trump, max_tricks)  for bid_tricks in range(1,8) 
							for max_tricks in range(14)
							for trump in range(5) ]

	pool = Pool()
	score_space = pool.map(score, input_space)
	pool.close()

	scorer = dict(zip(input_space, score_space))
	del input_space, score_space
	return scorer


scores = precompute_scores()
suit_offset = {0:3, 1:2, 2:1, 3:0, 4:4}

def get_score_vector(max_tricks):
	bid_vector = zeros(36)
	for occurence in max_tricks:
		for suit, trump in enumerate(occurence):
			for bid_tricks in range(1,8):
				bid_vector[(bid_tricks-1)*5 + suit_offset[suit] + 1] += scores[(bid_tricks, trump[0], trump[1])]
	return round(bid_vector / 5).astype(int)

def get_hand_vector(hand):
	hand_vector = zeros(52)
	for card in hand:
		hand_vector[13*card[0] + card[1] - 2] = 1
	return hand_vector

def vectorise_game(hand):
	hand["IMP"] = get_score_vector(hand["MaxTricks"]).tolist()
	hand["N"] = get_hand_vector(hand["N"]).tolist()
	hand["S"] = get_hand_vector(hand["S"]).tolist()
	del hand["MaxTricks"]
	return hand

def get_paths_from_command_line():
	parser = ArgumentParser()
        parser.add_argument("src")
        parser.add_argument("dest")
        args = parser.parse_args()
        return args.src, args.dest

def main():
        input_file, output_file = get_paths_from_command_line()
	with open(input_file, "r") as f:
		hands = load(f)
		hands = list(hands.values())
		pool = Pool()
		hands = list(pool.map(vectorise_game, hands))
		pool.close()
	with open(output_file,"w") as f:
		hands = {idx:hand for idx, hand in enumerate(hands)}
		dump(hands, f, indent=4)

main()
