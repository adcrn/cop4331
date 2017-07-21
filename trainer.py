from keras import backend as K
from keras.callbacks import Callback
from keras.utils import np_utils
from keras.models import Model
from keras.layers import (
	Activation,
	Convolution1D,
	Dense,
	Dropout,
	Input,
	Lambda,
	LSTM,
	MaxPooling1D,
	TimeDistributed,
	)
from keras.optimizers import Adam
from keras.utils import np_utils
from sklearn.model_selection import train_test_split as tts
import numpy as np
import os
import pickle


SEED = 4331    # random seed for the network
NUM_LAYERS = 3 # number of conv-act-pool layers before dropout
NUM_GENRES = 8
FILTER_LENGTH = 5
CONV_FILTER_COUNT = 256
LSTM_COUNT = 256
BATCH_SIZE = 32
EPOCH_COUNT = 100

def trainer(pickle):
	x = pickle['x']
	y = pickle['y']
	(x_training, x_validation, y_training, y_validation) = tts(x, y, test_size=0.3, random_state=SEED)

	print("Constructing Neural Network...")
	num_features = x_training.shape[2]
	input_shape = (None, num_features)
	model_input = Input(input_shape, name='input')
	layer = model_input

	for i in range(NUM_LAYERS):
		layer = Convolution1D(
			CONV_FILTER_COUNT,
			FILTER_LENGTH,
			)(layer)
		layer = Activation('relu')(layer)
		layer = MaxPooling1D(2)(layer)

	layer = Dropout(0.5)(layer)
	layer = LSTM(LSTM_COUNT, return_sequences=True)(layer)
	layer = Dropout(0.5)(layer)
	layer = TimeDistributed(Dense(NUM_GENRES))(layer)
	layer = Activation('softmax', name='output_realtime')(layer)

	# Gonna be real, this is black magic from Github and Stack Overflow.
	time_dist_merge = Lambda(
		function=lambda x: K.mean(x, axis=1), 
		output_shape=lambda shape: (shape[0],) + shape[2:],
		name='output_merged'
		)

	model_output = time_dist_merge(layer)
	model = Model(model_input, model_output)
	opt = Adam(lr=0.00001)
	model.compile(
		loss='categorical_crossentropy',
		optimizer=opt,
		metrics=['accuracy']
		)
	print("Neural Network Constructed.")

	print("Training...")
	model.fit(x_training, y_training, batch_size=BATCH_SIZE, epochs=EPOCH_COUNT,
			validation_data=(x_validation, y_validation), verbose=1)

	return model

data = pickle.load(open('data.pkl', 'rb'))

model = trainer(data)

with open('model.yaml', 'w') as f:
	f.write(model.to_yaml())

model.save_weights('weights.h5')