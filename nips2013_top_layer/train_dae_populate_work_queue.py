#!/bin/env python

import redis
import numpy as np

r_server = redis.Redis("localhost", 6379)

if not r_server.ping():
    print "Cannot ping server. Exiting."
    quit()


# When you want to use the dataset with d=100, you have to change
# - the pickle file used
# - the output_dir prefix
# - probably stuff like n_hiddens to reflect better the dimensionality


training_script_path = "/u/alaingui/umontreal/denoising_autoencoder/refactor_gp/models/train_dae.py"

d = None
train_samples_pickle = "/data/lisatmp2/alaingui/mnist/yann/yann_train_H1.pkl"
valid_samples_pickle = "/data/lisatmp2/alaingui/mnist/yann/yann_valid_H1.pkl"

experiment_name = "experiment_01_yann_mnist"

if (d == None) and train_samples_pickle == "/data/lisatmp2/alaingui/mnist/yann/yann_train_H1.pkl":

    L_n_hiddens = [128, 256]
    L_maxiter = [10]
    L_lbfgs_rank = [4,10]
    L_act_func = [ '["tanh", "sigmoid"]', '["sigmoid", "sigmoid"]']
    n_reps = 2

    S = [np.exp(s*np.log(10.0)) for s in np.linspace(1,0,5)] + [np.exp(s*np.log(10.0)) for s in np.linspace(0,-1,10)]
    #noise_stddevs = {'train' : [], 'valid' : [], 'wider_valid' : []
    noise_stddevs = {}
    noise_stddevs['train'] = [{'target':s, 'sampled':s} for s in S]
    noise_stddevs['valid'] = [{'target':s, 'sampled':s} for s in S]
    noise_stddevs['wider_valid'] = [{'target':s, 'sampled':10*s} for s in S]

else:
    quit()

output_dir_counter = 0

for n_hiddens in L_n_hiddens:
    for maxiter in L_maxiter:
        for lbfgs_rank in L_lbfgs_rank:
            for act_func in L_act_func:
                for r in range(n_reps):
                    output_dir = "/data/lisatmp2/alaingui/dae/dae_trained_models/mnist_yann_H1/%s/%0.6d" % (experiment_name, output_dir_counter)
                    output_dir_counter += 1

                    params = (training_script_path, n_hiddens, maxiter, lbfgs_rank, act_func, str(noise_stddevs).replace("'", '"'), train_samples_pickle, valid_samples_pickle, output_dir)
                    command = """python %s --n_hiddens=%d --maxiter=%d --lbfgs_rank=%d --act_func='%s' --noise_stddevs='%s' --train_samples_pickle="%s" --valid_samples_pickle="%s" --output_dir="%s" """ % params

                    print command
                    print
                    #r_server.rpush("train_gaussian_mixture", command)
