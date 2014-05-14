# -*- coding: utf-8 -*-

import numpy as np
import theano

from breze.learn import sgvb
from breze.learn.utils import theano_floatx


def test_vae():
    X = np.random.random((2, 10))
    X, = theano_floatx(X)

    m = sgvb.VariationalAutoEncoder(
        10, [20, 30], 4, [15, 25],
        ['tanh'] * 2, ['rectifier'] * 2,
        latent_prior='white_gauss',
        latent_posterior='diag_gauss',
        visible='bern',
        optimizer='rprop', batch_size=None,
        max_iter=3)

    m.fit(X)
    m.score(X)
    m.transform(X)
    m.denoise(X)
    m.estimate_nll(X[:2], 2)


def test_vae_imp_weight():
    X = np.random.random((2, 10))
    W = np.random.random((2, 1))
    X, W = theano_floatx(X, W)

    theano.config.compute_test_value = 'raise'

    m = sgvb.VariationalAutoEncoder(
        10, [20, 30], 4, [15, 25],
        ['tanh'] * 2, ['rectifier'] * 2,
        latent_prior='white_gauss',
        latent_posterior='diag_gauss',
        visible='bern',
        optimizer='rprop', batch_size=None,
        max_iter=3,
        imp_weight=True)
    m._init_pars()
    m._init_exprs()

    m.fit(X, W)
    m.score(X, W)
    m.transform(X)
    m.denoise(X)


def test_sequential_vae():
    theano.config.compute_test_value = 'warn'
    X = np.random.random((2, 5, 10))
    X, = theano_floatx(X)

    m = sgvb.VariationalSequenceAE(
        10, [20, 30], 4, [15, 25],
        ['tanh'] * 2, ['rectifier'] * 2,
        latent_prior='white_gauss',
        latent_posterior='diag_gauss',
        visible='bern',
        optimizer='rprop', batch_size=None,
        max_iter=3)

    m.fit(X)
    m.score(X)
    m.transform(X)
