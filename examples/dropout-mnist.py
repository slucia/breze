#! /usr/bin/env python
#! -*- coding: utf-8 -*-

__author__ = 'Justin Bayer, bayer.justin@googlemail.com'

import cPickle
import gzip
import sys

import numpy as np
import theano.tensor as T
import theano.tensor.nnet

from brummlearn.mlp import DropoutMlp
from brummlearn.utils import one_hot

import climin.stops


if __name__ == '__main__':
    n_epochs = 200
    batch_size = 100
    datafile = 'mnist.pkl.gz'

    # Load data.
    try:
        with gzip.open(datafile,'rb') as f:
            train_set, valid_set, test_set = cPickle.load(f)
    except IOError:
        print 'did not find mnist data set, you can download it from http://www.iro.umontreal.ca/~lisa/deep/data/mnist/mnist.pkl.gz'
        sys.exit(1)

    X, Z = train_set
    Z = one_hot(Z, 10)
    TX, TZ = test_set
    TZ = one_hot(TZ, 10)
    VX, VZ = valid_set
    VZ = one_hot(VZ, 10)

    net = DropoutMlp(
            784, [800, 800], 10, 
            hidden_transfers=['tanh'], out_transfer='softmax',
            loss='neg_cross_entropy',
            batch_size=batch_size,
            max_norm=15,
            #optimizer='lbfgs',
            max_iter=3000, verbose=True)

    print net.parameters.data.shape

    targets = T.argmax(net.exprs['target'], axis=1)
    predictions = T.argmax(net.exprs['output_in'], axis=1)
    incorrect = T.neq(targets, predictions).sum()
    f_incorrect_and_loss = net.function(['inpt', 'target'], ['loss', incorrect])

    f_output_in = net.function(['inpt'], 'output_in')

    every_kth = climin.stops.modulo_n_iterations(max(50000 / batch_size, 1))

    print 'starting training'
    for i, info in enumerate(net.iter_fit(X, Z)):
        if every_kth(info):
            net.parameters['in_to_hidden'] *= .2
            net.parameters['hidden_to_out'] *= .5 
            for j in range(len(net.n_hiddens) - 1):
                net.parameters['hidden_to_hidden_%i' % j] *= .5 

            train_error = f_incorrect_and_loss(X, Z)
            val_error = f_incorrect_and_loss(VX, VZ)
            test_error = f_incorrect_and_loss(TX, TZ)
            print '#%i' % (i * batch_size / X.shape[0]),
            print float(train_error[0]), int(train_error[1]),
            print float(val_error[0]), int(val_error[1]),
            print float(test_error[0]), int(test_error[1])
            print 'steprate', info['steprate'], 'momentum', info['momentum']

            net.parameters['in_to_hidden'] /= .2
            net.parameters['hidden_to_out'] /= .5 
            for j in range(len(net.n_hiddens) - 1):
                net.parameters['hidden_to_hidden_%i' % j] /= .5 

            step = info['step']
            print 'steps min max mean std', step.min(), step.max(), step.mean(), step.std()

            gradient = info['gradient']
            print 'gradient min max mean std', gradient.min(), gradient.max(), gradient.mean(), gradient.std()

            wrt = net.parameters.data
            print 'pars min max mean std', wrt.min(), wrt.max(), wrt.mean(), wrt.std()
        else:
            sys.stdout.write('.')
            sys.stdout.flush()
