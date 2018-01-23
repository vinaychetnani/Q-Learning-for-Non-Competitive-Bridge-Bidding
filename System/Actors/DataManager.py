import os
import numpy as np

class DataManager:

	def __init__(self, data_path, chunks = 12, hand_vector_size = 52, monotonic_penalty = 0.0):
		"""
		Initialises the vectorised data loader.
		Parameters:
			Necessary:
				data_path: Expects something like "DataPath-{}.npy".
			Optional:
				chunks: The total number of chunks the data is split into.
				hand_vector_size: Size of the hand feature vector.
				monotonic_penalty: Penalty to enforce monotonically increasing bids constraint.
		"""
		self.data_path = data_path
		self.chunks = chunks
		self.hand_vector_size = hand_vector_size
		self.monotonic_penalty = monotonic_penalty

		self.N = None
		self.S = None
		self.IMP = None
		self.BidHistory = None
		self.X = None
		self.PrevBid = None

	def load(self, episode):
		"""
		Loads the data from the vectorised hand data.
		Also automatically resets BidHistory.
		Parameters:
			Necessary:
				episode: Episode of the training.
		"""
		path = self.data_path.format(episode % self.chunks)
		raw_data = np.load(path)

		self.N = raw_data[:, :self.hand_vector_size]
		self.S = raw_data[:, self.hand_vector_size : 2 * self.hand_vector_size]
		self.IMP = raw_data[:, 2 * self.hand_vector_size:]

		self.BidHistory = np.zeros(self.IMP.shape)
		self.PrevBid = np.ones(self.N.shape[0], dtype = np.int16) * -1

	def concatenate_data(self, step):
		"""
		Concatenates the appropriate hand with the bidding history.
		Parameters:
			Necessary:
				step: Step in the bidding sequence.
		"""
		if step % 2 == 0:
			self.X = np.concatenate([self.N, self.BidHistory], axis = 1)
		else:
			self.X = np.concatenate([self.S, self.BidHistory], axis = 1)

	def save_data(self, data_path):
		"""
		Saves the data in the appropriate format for training.
		Parameters:
			Necessary:
				data_pata: Directory to save training data to.
		"""
		np.save(os.path.join(data_path, "Train_X.npy"), self.X)
		np.save(os.path.join(data_path, "Train_Y.npy"), self.IMP)

	def update_bid_history(self):
		"""
		Updates the bidding history given the previous bid.
		"""
		self.BidHistory[range(len(self.PrevBid)), np.asarray(self.PrevBid, dtype = int)] = 1

	def remove_completed_sequences(self):
		"""
		Remove all bidding sequences that have completed.
		"""
		uncompleted_idx_mask = np.logical_and(self.PrevBid != 35, self.PrevBid != 0)
		self.N = self.N[uncompleted_idx_mask]
		self.S = self.S[uncompleted_idx_mask]
		self.IMP = self.IMP[uncompleted_idx_mask]
		self.BidHistory = self.BidHistory[uncompleted_idx_mask]
		self.X = self.X[uncompleted_idx_mask]
		self.PrevBid = self.PrevBid[uncompleted_idx_mask]

	def penalise_smaller_bids(self):
		"""
		Given the previous bid it penalises all smaller bids, ensuring the system learns
		the monotonically increasing nature of bids.
		"""
		for idx in range(len(self.PrevBid)):
			self.IMP[idx,:int(self.PrevBid[idx])] = self.monotonic_penalty

	def pre_step(self, step, data_path):
		"""
		Handle one pre-prediction step of an episode.
		Parameters:
			Necessary:
				step
				data_path
		"""
		self.concatenate_data(step)
		self.save_data(data_path)

	def post_step(self):
		"""
		Handles one post-prediction step of an episode.
		"""
		self.update_bid_history()
		self.remove_completed_sequences()
		self.penalise_smaller_bids()

