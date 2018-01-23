import os
from argparse import ArgumentParser
from operator import itemgetter

from Actors import *

class System:

	def __init__(self):
		"""
		Initialises the system.
		"""
		self.step = 0
		self.episode = 0
		self.parser = ArgumentParser()
		self.args = None
		self.predictor = None
		self.bandit = None
		self.trainer = None


	def setup_arguments(self):
		"""
		Sets up the argument parser.
		"""
		self.parser.add_argument("--epsilon", help = "Greediness of Bandit",
					default = 0.1)
		self.parser.add_argument("--input_size", help = "Size of Neural Network Input",
					default = 88)
		self.parser.add_argument("--layers", help = "Number of Layers of Neural Network",
					default = 2)
		self.parser.add_argument("--units", help = "Number of Units of Neural Network",
					default = 30)
		self.parser.add_argument("--output_size", help = "Size of Output of Neural Network",
					default = 36)
		self.parser.add_argument("--epochs", help = "Number of Epochs to Train the Agent",
					default = 10)
		self.parser.add_argument("--max_steps", help = "Maximum Length of Bidding Sequence",
					default = 8)
		self.parser.add_argument("--max_episodes", help = "Maximum Number of Episodes",
					default = 4)
		self.parser.add_argument("--base_dir", help = "Path to Base Directory",
					default = "/scratch/ee/btech/ee3140629/BridgeBidding")
		self.parser.add_argument("--raw_data_path", help = "Path for Raw Hand Data Relative to Base Directory", 
					default = "Data/Test/Data-{}.npy")
		self.parser.add_argument("--data_dir", help = "Directory String for Training Data Relative to Base Directory",
					default = "EpisodeData/Train/{}-{}/{}-{}")
		self.parser.add_argument("--checkpoint_dir", help = "Directory String for Checkpoint Data Relative to Base Directory",
					default = "Checkpoints/Train/{}-{}/{}-{}")
		self.args = self.parser.parse_args()


	def setup_episode(self):
		"""
		Finds last episode trained
		"""
		try:
			episode_step = [folder.split("-") for folder in os.listdir(
				os.path.join(self.args.base_dir, "Checkpoints/Train/{}-{}".format(self.args.layers, self.args.units)))]
			episode_step = [(int(folder[0]), int(folder[1])) for folder in episode_step]
			episode_step = sorted(episode_step, key = itemgetter(0), reverse = True)
			episode_step = [folder for folder in episode_step if folder[0] == episode_step[0][0]]
			episode_step = sorted(episode_step, key = itemgetter(1), reverse = True)
			episode_step = episode_step[0]
			self.episode,_ = episode_step
		except:
			pass


	def setup_actors(self):
		"""
		Sets up the predictor and the trainer
		"""
		self.predictor = Agent(self.args.input_size, self.args.layers, self.args.units, self.args.output_size, "predict")
		self.trainer = Agent(self.args.input_size, self.args.layers, self.args.units, self.args.output_size, "train", epochs = self.args.epochs)
		self.data_manager = DataManager(os.path.join(self.args.base_dir, self.args.raw_data_path))
		self.bandit = EpsilonBandit(self.args.epsilon)


	def setup(self):
		"""
		Sets up the neural networks for the agent.
		"""
		self.setup_arguments()
		self.setup_episode()
		self.setup_actors()


	def episode_step(self):
		"""
		Sets the stage for the next episode.
		"""
		print("Starting Episode {}".format(self.episode))
		self.data_manager.load(self.episode)
		self.episode = self.episode + 1
		self.step = 0


	def bid_step(self):
		"""
		Takes a step in the bidding sequence.
		"""
		data_path = os.path.join(self.args.base_dir, 
				self.args.data_dir.format(self.args.layers, self.args.units, self.episode, self.step))
		if self.step == 0:
			checkpoint_path = os.path.join(self.args.base_dir, 
						self.args.checkpoint_dir.format(self.args.layers, self.args.units, self.episode - 1, self.args.max_steps - 1))
		else:
			checkpoint_path = os.path.join(self.args.base_dir,
						self.args.checkpoint_dir.format(self.args.layers, self.args.units, self.episode, self.step - 1))

		self.predictor.setup(data_path, checkpoint_path)
		self.data_manager.pre_step(self.step, data_path)
		predictions = self.predictor.predict_model(self.data_manager.X)
		self.data_manager.PrevBid = self.bandit.decision(predictions, self.data_manager.PrevBid)
		self.data_manager.post_step()

	
	def train_step(self):
		"""
		Trains the model after the given step.
		"""	
		data_path = os.path.join(self.args.base_dir, 
					self.args.data_dir.format(self.args.layers, self.args.units, self.episode, self.step))
		checkpoint_path = os.path.join(self.args.base_dir, 
					self.args.checkpoint_dir.format(self.args.layers, self.args.units, self.episode, self.step))
		self.trainer.setup(data_path, checkpoint_path)
		self.trainer.train_model()


	def complete_step(self):
		"""
		Takes a step in the bidding sequence and trains the model.
		"""
		print("\tStarting Step {}".format(self.step))
		self.bid_step()
		self.train_step()
		self.step = self.step + 1

	def test(self):
		"""
		Takes the steps in the bidding sequence for a given set of data points.
		"""
		import numpy as np

		score = 0

		def score_completed_sequences(predictions):
			completed_idx_mask = np.logical_or(self.data_manager.PrevBid == 35, self.data_manager.PrevBid == 0)
			IMP = self.data_manager.IMP[completed_idx_mask]
 			pred = predictions[completed_idx_mask]
			return np.sum(IMP[range(IMP.shape[0]), [int(predx) for predx in pred]])

		def score_remaining_sequences(predictions):
			IMP = self.data_manager.IMP
 			pred = predictions
			return np.sum(IMP[range(IMP.shape[0]), [int(predx) for predx in pred]])

		data_path = os.path.join(self.args.base_dir, 
				self.args.data_dir.format(self.args.layers, self.args.units, self.episode, self.step))
		checkpoint_path = os.path.join(self.args.base_dir,
				self.args.checkpoint_dir.format(self.args.layers, self.args.units, self.episode - 1, self.args.max_steps - 1))
		self.predictor.setup(data_path, checkpoint_path)

		for _ in range(self.args.max_steps - 1):
			self.data_manager.pre_step(self.step, data_path)
			predictions = self.predictor.predict_model(self.data_manager.X)
			self.data_manager.PrevBid = self.bandit.decision(predictions, self.data_manager.PrevBid)
			score += score_completed_sequences(self.data_manager.PrevBid)
			self.data_manager.post_step()

		self.data_manager.pre_step(self.step, data_path)
		predictions = self.predictor.predict_model(self.data_manager.X)
		self.data_manager.PrevBid = self.bandit.decision(predictions, self.data_manager.PrevBid)
		score += score_remaining_sequences(self.data_manager.PrevBid)

		print(score / 10000)	
