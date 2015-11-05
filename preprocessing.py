from __future__ import absolute_import
import numpy as np
import os
import h5py
from scipy.stats import zscore
from utils import rolling_window

__all__ = ['datagen']


def datagen(cellidx, batchsize, expt='15-10-07', filename='naturalscene', method='train', history=40):
    """
    Returns a generator that yields batches of data

    Parameters
    ----------

    cellidx : int
        Which cell to train on

    batchsize : int
        How many samples to include in each batch

    expt : string, optional
        The experiment to load (currently only works with 15-10-07)

    filename : string, optional
        The name of the file to load ('naturalscene' or 'whitenoise')

    method : string, optional
        Either 'train' or 'test' for the class/type of data to load

    history : int, optional
        How many points to include in the filter history

    """

    # currently only works with the Oct. 07, 15 experiment
    if expt == '15-10-07':
        pass
    else:
        raise NotImplementedError('Did not recognize experiment: ' + str(expt))

    # custom data directories for different machines based on OS hostname
    datadirs = {
        'mbp': os.path.expanduser('~/experiments/data/'),
        'lenna': os.path.expanduser('~/experiments/data/')
    }

    # load the hdf5 file
    f = h5py.File(os.path.join(datadirs[os.uname()[1]], expt, filename + '.h5'), 'r')

    # load the stimulus
    stim = np.array(f[method]['stimulus']).astype('float32')

    # reshaped stimulus (nsamples, time/channel, space, space)
    stim_reshaped = np.rollaxis(np.rollaxis(rolling_window(stim, history, axis=0), 2), 3, 1)

    # get the response for this cell
    resp = np.array(f[method]['response/firing_rate_10ms'][cellidx, history:])

    # keep looping over epochs
    num_batches = int(np.floor(float(resp.size) / batchsize))
    while True:

        # reshuffle indices for this new epoch
        indices = np.arange(resp.size)
        np.random.shuffle(indices)
        indices = indices[:(batchsize * num_batches)].reshape(num_batches, batchsize)

        for batch_idx in range(num_batches):

            # select random indices for this batch
            inds = indices[batch_idx]

            # yield data
            yield zscore(stim_reshaped[inds, ...]), resp[inds]
