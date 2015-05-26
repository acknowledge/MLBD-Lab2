# -*- coding: utf-8 -*-
"""
Created on Tue May 12 12:51:17 2015

@author: simo
"""

import numpy as np
import matplotlib.pyplot as pl
from matplotlib import cm
from loadData import  readFile, extractArrays

fname = 'data3/data10.json'

infos = readFile(fname)
titles, words, matrix = extractArrays(infos)
#matrix = np.transpose(matrix)

pl.figure(figsize=(20,40))
pl.xticks(np.arange(matrix.shape[1]*2), words, rotation=45)
pl.yticks(np.arange(matrix.shape[0]*2), titles)
pl.title("titles")
pl.imshow(matrix, interpolation='nearest', cmap=cm.binary)
_ = pl.savefig('images/titles.png')


import kohonen
from Utils import computeUMatrix, constructSamplesForNeurons, ExponentialTimeseries as ET
from random import shuffle

## define cosine metric for configure distance metrix on kohonen
def cosine_metric(x, y):
    '''Returns the cosine distance between x and y.'''
    nx = np.sqrt(np.sum(x * x, axis=-1))
    ny = np.sqrt(np.sum(y * y, axis=-1))
    # the cosine metric returns 1 when the args are equal, 0 when they are
    # orthogonal, and -1 when they are opposite. we want the opposite effect,
    # and we want to make sure the results are always nonnegative.
    return 1 - np.sum(x * y, axis=-1) / nx / ny
## Initializes the Kohonen map as a rectangular map of len(titles) x len(titles)*2
side = len(titles)
side=side/2
params = kohonen.Parameters(dimension=len(words), shape=(side,side*2), metric=cosine_metric)
kmap = kohonen.Map(params)

## Learns the dataset n_iter times in a randomly defined order
## The learning rate decreases exponentially from 1 to 0.2
n_iter = 20
kmap._learning_rate = ET(1, 0.2, n_iter*matrix.shape[0])
kmap._neighborhood_size = ET(4./3*side, 1, n_iter*matrix.shape[0])
for i in range(0,n_iter):
    order = np.arange(0, matrix.shape[0], 1)
    shuffle(order)
    for j in order:
        kmap.learn(matrix[j])

## Computes distance between neurons and creates a U-Matrix (of 2*len(titles) x len(titles)*4)
u_matrix = computeUMatrix(kmap)

# Creates a colormap for the U-Matrix
colors = cm.Spectral_r
colors.set_bad('w',1.)

## Gets winning neuron for each sample (1-nn)
filmDict = constructSamplesForNeurons(kmap, matrix)

## Prints U-Matrix
fig = pl.figure(figsize=(20,30))

pl.imshow(u_matrix, cmap=colors, interpolation="nearest")
pl.colorbar(shrink=0.2)

## Prints titles on map
for neuron in filmDict:
    neuronx, neurony = neuron.split(",")
    neuronx = int(neuronx) * 2
    neurony = int(neurony) * 2
    pl.scatter(neurony, neuronx)
    filmNames = ""
    for filmID in filmDict[neuron]:
        filmNames += titles[filmID] + "\n"
    pl.annotate(filmNames, (neurony, neuronx), size=6)

pl.axis('off')

_ = pl.savefig("images/map10.png", bbox_inches = 'tight')