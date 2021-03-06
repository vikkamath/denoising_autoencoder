

import numpy as np
import sys, os
import cPickle

import refactor_gp
import refactor_gp.models
from   refactor_gp.models import dae_untied_weights

import matplotlib
# This has already been specified in .scitools.cfg
# so we don't need to explicitly pick 'Agg'.
# matplotlib.use('Agg')
import pylab
import matplotlib.pyplot as plt

def core(pickled_dae_dir):

    # We read from the trained dae directory two things :
    #   - the dae itself
    #   - the path for the training samples

    assert os.path.exists(os.path.join(pickled_dae_dir, "trained_dae.pkl"))
    assert os.path.exists(os.path.join(pickled_dae_dir, "extra_details.pkl"))


    extra_details_contents = cPickle.load(open(os.path.join(pickled_dae_dir, "extra_details.pkl"), "r"))
    train_samples_pickle = extra_details_contents['train_samples_pickle']
    assert os.path.exists(train_samples_pickle)
    train_samples = cPickle.load(open(train_samples_pickle, "r"))

    # Right now we're only interested in plotting quiver plots
    # for data of dimension 2.
    assert train_samples.shape[1] == 2

    # irrelevant values because we load a pickle anyways
    mydae = dae_untied_weights.DAE_untied_weights(n_inputs = 1,
                                                  n_hiddens = 1,
                                                  act_func = ['tanh', 'tanh'])
    mydae.load_pickle(os.path.join(pickled_dae_dir, "trained_dae.pkl"))

    def r(x):
        # only asserted because that's what we expect,
        # not asserted because it would produce some conceptual
        # problem
        assert len(x.shape) == 1
        return mydae.encode_decode(x.reshape((1,-1))).reshape((-1,))

    output_file = os.path.join(pickled_dae_dir, "reconstruction_grid_dimensions_0_and_1.png")
    plot_samples_and_r_grid(train_samples[0:500,:], r, output_file, dpi = 300)
    print "Wrote %s" % (output_file,)

    output_file = os.path.join(pickled_dae_dir, "reconstruction_grid_dimensions_0_and_1_wider.png")
    plot_samples_and_r_grid(train_samples[0:500,:], r, output_file, dpi = 300, window_width_scaling = 2.0)
    print "Wrote %s" % (output_file,)


def usage():
    print "python plot_quiver_for_2d_dae.py --pickled_dae_dir=/data/lisatmp2/alaingui/dae/dae_trained_models/gaussian_mixture_d2/experiment_11/000000"


def main(argv):
    """

    """

    import getopt

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv", ["pickled_dae_dir="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    pickled_dae_dir = None

    verbose = False
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("--pickled_dae_dir"):
            pickled_dae_dir = a
        else:
            assert False, "unhandled option"

    assert pickled_dae_dir
    assert os.path.exists(pickled_dae_dir)
    return core(pickled_dae_dir)


def plot_samples_and_r_grid(samples, r, outputfile, plotgrid_N_buckets = 30, dpi = 150, window_width_scaling = 1.0):

    #center = samples.mean(axis=1)
    center = (   (samples[:,0].max() + samples[:,0].min())/2,   (samples[:,1].max() + samples[:,1].min()/2)   )
    print "centers are (%f, %f)" % (center[0], center[1])

    window_width = window_width_scaling*(samples.max() - samples.min())
    print "window_width is %f" % (window_width,)

    (plotgrid_X, plotgrid_Y) = np.meshgrid(np.arange(center[0] - window_width,
                                                     center[0] + window_width,
                                                     2 * window_width / plotgrid_N_buckets),
                                           np.arange(center[1] - window_width,
                                                     center[1] + window_width,
                                                     2 * window_width / plotgrid_N_buckets))
    plotgrid = np.vstack([np.hstack(plotgrid_X), np.hstack(plotgrid_Y)]).T

    # Not sure it's worth truncating some elements now that we're
    # producing more plots.
    #    D = np.sqrt(plotgrid[:,0]**2 + plotgrid[:,1]**2)
    #    plotgrid = plotgrid[D<0.7]
    #    print plotgrid_X.shape
    #    print plotgrid_Y.shape
    #    print "Will keep only %d points on the plotting grid after starting from %d." % (plotgrid.shape[0], plotgrid_X.shape[0])

    print "Making predictions for the grid."

    grid_pred = np.vstack( [r(e) for e in plotgrid] )

    grid_error = np.sqrt(((grid_pred - plotgrid)**2).sum(axis=1)).mean()
    print "grid_error = %0.6f (not necessarily a relevant information)" % grid_error

    print "Generating plot."

    pylab.hold(True)
    pylab.scatter(samples[:,0], samples[:,1], c='#f9a21d')
    
    arrows_scaling = 1.0
    pylab.quiver(plotgrid[:,0],
                 plotgrid[:,1],
                 arrows_scaling * (grid_pred[:,0] - plotgrid[:,0]),
                 arrows_scaling * (grid_pred[:,1] - plotgrid[:,1]))
    pylab.draw()
    pylab.axis([center[0] - window_width*1.0, center[0] + window_width*1.0,
                center[1] - window_width*1.0, center[1] + window_width*1.0])
    pylab.savefig(outputfile, dpi=dpi)
    pylab.close()

    return grid_error


if __name__ == "__main__":
    main(sys.argv)