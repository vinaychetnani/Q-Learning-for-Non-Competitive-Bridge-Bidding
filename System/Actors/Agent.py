import os
import json
from operator import itemgetter

import numpy as np
import tensorflow as tf

from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, BatchNormalization
from keras.callbacks import ModelCheckpoint
from keras.models import load_model

class Agent:

	def __init__(self, input_size, layers, units, output_size, mode,
			dropout_prob = 0.2, val_split = 0.2, epochs = 20 ):
		"""
		Initialises the neural network for mapping from state to action spaces.
		The model consists of a series of (Leaky ReLU, Dropout, BatchNorm) layers.
		In case mode == test, dropout probability is 0.
		The data directory must be organised as data_dir/X_train.npy and data_dir/Y_train.npy
		Parameters:
			Necessary: 
				Input Size
				Number of Hidden Layers
				Units is Each Hidden Layer
				Output Size
				Mode (train/predict)
			Optional:
				Dropout Probability (Probability that Neuron is to be Dropped)
					Default = 0.2
				Validation Split Fraction
					Default = 0.2
				Epochs to Train For
					Default = 20
		"""
		self.input_size = input_size
		self.layers = layers
		self.units = units
		self.output_size = output_size
		self.mode = mode
		self.dropout_prob = dropout_prob
		self.val_split = val_split
		self.epochs = epochs
		self.data_dir = None
		self.checkpoint_dir = None
		self.model = None

		assert self.input_size > 0
		assert self.layers > 1
		assert self.units > 0
		assert self.output_size > 0
		assert self.dropout_prob >= 0 and self.dropout_prob < 1
		assert self.val_split >= 0 and self.val_split < 1
		assert self.mode in ["train", "predict"]

		if self.mode == "predict":
			self.dropout_prob = 0

		if self.mode == "train":
			self.X_train = None
			self.Y_train = None


	def set_directories(self, data_dir, checkpoint_dir):
		"""
		Sets the directories for the data and checkpoints.
		Parameters:
			Necessary:
				Data Directory
				Checkpoint Directory
		"""
		self.data_dir = data_dir
		self.checkpoint_dir = checkpoint_dir

		if not os.path.exists(data_dir):
			os.makedirs(data_dir)

		if not os.path.exists(checkpoint_dir):
			os.makedirs(checkpoint_dir)


	def build_model(self):
		"""
		Builds the model to be used.
		"""
		self.model = Sequential()
		self.model.add(Dense(self.units, input_dim = self.input_size, 
					kernel_initializer = "truncated_normal", 
					bias_initializer = "truncated_normal"))
		self.model.add(Activation("relu"))
		self.model.add(Dropout(self.dropout_prob))
		self.model.add(BatchNormalization())
		if self.layers > 2:
			for i in range(self.layers - 2):
				self.model.add(Dense(self.units, 
								kernel_initializer='truncated_normal', 
								bias_initializer='truncated_normal'))
				self.model.add(Activation("relu"))
				self.model.add(Dropout(self.dropout_prob))
				self.model.add(BatchNormalization())
		self.model.add(Dense(self.output_size))
		self.model.add(Activation("relu"))


	def compile_model(self):
		"""
		Compiles the model with a MSE loss and an Adam optimizer.
		"""
		self.model.compile(optimizer = "adam", loss = "mse")


	def load_train_data(self):
		"""
		Loads the required data as per the mode.
		"""
		data_path = os.path.join(self.data_dir, "Train_X.npy")
		self.X_train = np.load(data_path)
		data_path = os.path.join(self.data_dir, "Train_Y.npy")
		self.Y_train = np.load(data_path)


	def load_best_checkpoint(self):
		"""
		Loads the best checkpoint from the checkpoint directory.
		"""
		checkpoints = [file for file in os.listdir(self.checkpoint_dir)
				if file.endswith(".hdf5")]
		if len(checkpoints) > 0:
			checkpoints = [(ckpt, float(ckpt[:-5].split("-")[-1]))
					for ckpt in checkpoints]
			checkpoints = sorted(checkpoints, key = itemgetter(1), reverse = False)

			checkpoint = os.path.join(self.checkpoint_dir, checkpoints[0][0])
			self.model = load_model(checkpoint)
			print("\tLoaded checkpoint {}".format(checkpoint))
		else:
			print("\tStarting Afresh {}".format(self.checkpoint_dir))


	def setup(self, data_dir, checkpoint_dir):
		"""
		Sets the necesary directories for data and checkpoints.
		Sets up the model by building and compiling it, as well as loading the data.
		In case the model is to be tested, the best checkpoint is loaded as well.
		Parameters:
			Necessary:
				Data Directory
				Checkpoint Directory
		"""
		self.set_directories(data_dir, checkpoint_dir)
		self.build_model()
		self.compile_model()

		if self.mode == "train":
			self.load_train_data()

		if self.mode == "predict":
			self.load_best_checkpoint()

			
	def train_model(self):
		"""
		Trains the model and saves the best checkpoint to the checkpoint directory.
		It also saves the history as a json to the checkpoint directory.
		"""
		checkpoint_path = os.path.join(self.checkpoint_dir, "{epoch:02d}-{val_loss:.4f}.hdf5")
		checkpointer = ModelCheckpoint(filepath = checkpoint_path, save_best_only = False, verbose = 0)
		history = self.model.fit(self.X_train, self.Y_train, validation_split = self.val_split, 
				epochs = self.epochs, callbacks=[checkpointer], verbose=0)
		with open(os.path.join(self.checkpoint_dir, "history.json"), "w") as f:
			json.dump(history.history, f, indent = 4)


	def predict_model(self, X):
		"""
		Given a set of data points, this function returns the corresponding predictions.
		"""
		return self.model.predict(X)
