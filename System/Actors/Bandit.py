import numpy as np
from multiprocessing import Pool

class EpsilonBandit:
	def __init__(self, epsilon):
		"""
		Initialises the epsilon greedy bandit.
		Parameters: 
			epsilon: Probability of choosing a non optimal action
		"""
		self.epsilon = epsilon
		assert epsilon >= 0 and epsilon < 1

	def decision(self, options, prev_bid):
		"""
		Takes a decision based on the relative merit of the options and the previous bid (ensuring legality of the bid made)
		Parameters:
			options: A Episode_Size * 36 Matrix
			prev_bid: A Episode_Size-Dimensional Vector
		"""

		assert options.shape[1] == 36
		assert np.min(prev_bid) >= -1 and np.max(prev_bid) < 35

		# prev_bid is limited to len(options) - 1 because the choice has to be made from options[prev_bid+1:]

		choice = np.random.choice(np.arange(0, 2), size = prev_bid.shape,
									p = [self.epsilon, 1 - self.epsilon] )

		bid = np.zeros(prev_bid.shape)

		for idx in range(len(choice)):		
			if choice[idx] == 0:
				offset = int(prev_bid[idx] + 1)
				bid[idx] = np.argmax(options[idx][offset:]) + offset
				if(options[idx][0] >= options[idx][int(bid[idx])]):
					bid[idx] = 0
			else:
				bid[idx] = np.random.randint(prev_bid[idx],36)

		return bid
