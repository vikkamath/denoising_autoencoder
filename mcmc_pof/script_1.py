

import time, os, sys, getopt
import numpy as np

import metropolis_hastings_sampler

def usage():
    print "-- usage example --"
    print "python script_1.py --n_samples=100 --n_chains=1000 --thinning_factor=100 --langevin_lambda=0.01 --mcmc_method=metropolis_hastings_langevin_E --dataset=ninja_star"

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv", ["help", "omit_ninja_star_from_plots", "n_samples=", "n_chains=", "thinning_factor=", "burn_in=", "langevin_lambda=", "mcmc_method=", "proposal_stddev=", "dataset=", "output_dir_prefix=", "reference_pickled_samples_for_KL=", "reference_stddev_for_KL=", "no_plots"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    sampling_options = {}
    sampling_options["n_chains"] = None
    sampling_options["no_plots"] = False

    output_options = {}

    verbose = False
    for o, a in opts:
        if o == "-v":
            # unused
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        if o == "--no_plots":
            sampling_options["no_plots"] = True
        elif o in ("--n_samples"):
            sampling_options["n_samples"] = int(a)
        elif o in ("--thinning_factor"):
            sampling_options["thinning_factor"] = int(a)
        elif o in ("--burn_in"):
            sampling_options["burn_in"] = int(a)
        elif o in ("--langevin_lambda"):
            sampling_options["langevin_lambda"] = float(a)
        elif o in ("--proposal_stddev"):
            sampling_options["proposal_stddev"] = float(a)
        elif o in ("--n_chains"):
            sampling_options["n_chains"] = int(a)
        elif o in ("--mcmc_method"):
            sampling_options["mcmc_method"] = a
            #if not a in ['langevin',
            #             'metropolis_hastings_langevin_E',
            #             'metropolis_hastings_langevin_grad_E',
            #             'metropolis_hastings_E',
            #             'metropolis_hastings_grad_E']:
            #    error("Bad name for mcmc_method.")
        elif o in ("--dataset"):
            if a == 'ninja_star':
                import ninja_star_distribution
                sampling_options["dataset_description"] = "ninja_star"
                sampling_options["E"] = ninja_star_distribution.E
                sampling_options["grad_E"] = ninja_star_distribution.grad_E
            if a == 'butterfly':
                import butterfly_distribution
                sampling_options["dataset_description"] = "butterfly"
                sampling_options["E"] = butterfly_distribution.E
                sampling_options["grad_E"] = butterfly_distribution.grad_E
            else:
                "Unrecognized dataset."
        elif o in ("--output_dir_prefix"):
            output_options['output_dir_prefix'] = a
        elif o in ("--reference_pickled_samples_for_KL"):
            output_options['reference_pickled_samples_for_KL'] = a
        elif o in ("--reference_stddev_for_KL"):
            output_options['reference_stddev_for_KL'] = float(a)
        elif o in ("--omit_ninja_star_from_plots"):
            output_options['omit_ninja_star_from_plots'] = True
        else:
            assert False, "unhandled option"

    if sampling_options["dataset_description"] == "ninja_star":
        if not sampling_options["n_chains"] == None:
            sampling_options["x0"] = np.random.normal(size=(sampling_options["n_chains"],2))
        else:
            sampling_options["x0"] = np.random.normal(size=(2,))
        
        # osbsolete
        #output_options["cross_entropy_function"] = ninja_star_distribution.cross_entropy

    elif sampling_options["dataset_description"] == "butterfly":
        if not sampling_options["n_chains"] == None:
            sampling_options["x0"] = np.random.normal(size=(sampling_options["n_chains"],2))
        else:
            sampling_options["x0"] = np.random.normal(size=(2,))
    else:
        error("No dataset was supplied.")


    results = metropolis_hastings_sampler.mcmc_generate_samples(sampling_options)
    #
    # Returns a dictionary of this form.
    #
    # {'samples': numpy array (n_chains, n_samples, d),
    #  'elapsed_time': seconds as float,
    #  'proposals_per_second': float,
    #  'acceptance_ratio': float in [0.0,1.0] }

    print "Got the samples. Acceptance ratio was %f" % results['acceptance_ratio']
    print "MCMC proposal speed was 10^%0.2f / s" % (np.log(results['proposals_per_second']) / np.log(10), )


    if len(results['samples'].shape) == 2:

        # We will evaluate an approximate KL divergence if we are given a
        # reference set of samples from the true distribution.
        if output_options.has_key("reference_pickled_samples_for_KL"):

            import KL_approximation
            import cPickle
            assert os.path.exists(output_options["reference_pickled_samples_for_KL"])
            f = open(output_options["reference_pickled_samples_for_KL"])
            reference_sample = cPickle.load(f)

            # Let's leave out that argument for now.
            #if output_options.has_key("reference_stddev_for_KL"):
            #    reference_stddev_for_KL = output_options["reference_stddev_for_KL"]
            #else:
            #    reference_stddev_for_KL = None

            KL_value = KL_approximation.KL(reference_sample, results['samples'], 0.5, 0.5)
            print "We got a KL divergence value of %f" % KL_value


    output_image_dir = "%s/%s/%d" % (output_options["output_dir_prefix"], sampling_options['mcmc_method'], int(time.time()) )
    os.makedirs(output_image_dir)

    import cPickle
    output_pkl_name = os.path.join(output_image_dir, "results_and_params.pkl")
    f = open(output_pkl_name, "w")
    if sampling_options.has_key("grad_E"):
        sampling_options["grad_E"] = "CANNOT BE PICKLED"
    cPickle.dump({'results':results, 'sampling_options':sampling_options, 'output_options':output_options}, f)
    f.close()
    print "Wrote " + output_pkl_name


    samples_only_pkl_name = os.path.join(output_image_dir, "samples.pkl")
    f = open(samples_only_pkl_name, "w")
    cPickle.dump(results['samples'], f)
    f.close()
    print "Wrote " + samples_only_pkl_name


    if sampling_options["dataset_description"] == "ninja_star" and not (sampling_options["no_plots"]):

        if len(results['samples'].shape) == 2:
    
            output_image_path = os.path.join(output_image_dir, "whole_chain.png")
            plot_one_slice_of_ninja_star_samples(results['samples'],
                                                 output_image_path,
                                                 dpi=200,
                                                 omit_ninja_star_from_plots = output_options.has_key('omit_ninja_star_from_plots'))

        elif len(results['samples'].shape) == 3:

            #plot_one_slice_of_ninja_star_samples_2(results['samples'],
            #                                     lambda n : os.path.join(output_image_dir, "frame_%0.6d.png" % n),
            #                                     dpi=100)

            for n in np.arange(sampling_options['n_samples']):
                output_image_path = os.path.join(output_image_dir, "frame_%0.6d.png" % n)
                plot_one_slice_of_ninja_star_samples(results['samples'][:,n,:],
                                                     output_image_path,
                                                     dpi=100,
                                                     omit_ninja_star_from_plots = output_options.has_key('omit_ninja_star_from_plots'))

                import subprocess
                #export MOVIEDIR=${HOME}/Documents/tmp/metropolis_hastings_E/1359965409
                #ffmpeg -i ${MOVIEDIR}/frame_%06d.png -vcodec libx264 -vpre hq -crf 22 -r 10 ${MOVIEDIR}/seq.mp4
                subprocess.check_output(["ffmpeg", "-i", output_image_dir + r"/frame_%06d.png", "-y", "-vcodec", "libx264", "-vpre", "hq", "-crf", "22", "-r", "10", output_image_dir + r"/assembled.mp4"])

            print "Generated movie at %s." % (output_image_dir + r"/assembled.mp4", )
        else:
            raise("Wrong shape for samples returned !")
    


# We'll put the imports here just in case the
# global scope wouldn't be the best idea.
import matplotlib
matplotlib.use('Agg')
import pylab
import matplotlib.pyplot as plt


def plot_one_slice_of_ninja_star_samples(samples_slice, output_image_path, dpi=100, omit_ninja_star_from_plots = False):
    """
        Samples should be of size (M, d).
        You would generally pick either one chain alone
        or one time slice from a set of chains.

        This plotting function doesn't pretend to be
        a very general method. It assumes that the samples
        are 2-dimensional and that [-4.0, 4.0]^2 is the
        best choice of window to plot the samples.
    """

    import ninja_star_distribution

    pylab.hold(True)

    x = samples_slice[:,0]
    y = samples_slice[:,1]

    # TODO : pick better color for the sample dots
    pylab.scatter(x, y)

    # TODO : stamp the KL divergence on the plots

    M = 4.0
    if not omit_ninja_star_from_plots:
        print "Computing the original pdf values."

        mesh_x,mesh_y = np.mgrid[-M:M:.01, -M:M:.01]
        z = ninja_star_distribution.mesh_pdf(mesh_x, mesh_y)

        print "Generating the nice plots."
        model_pdf_values_plot_handle = plt.pcolor(mesh_x, mesh_y, z)
        #plt.winter()
        plt.pink()
        #d = plt.colorbar(model_pdf_value_plot_handle, orientation='horizontal')

    pylab.axes([-M, M, -M, M])
    count_of_points_outside = np.count_nonzero( (x < M) + (M < x) + (y < M) + (M < y) )
    pylab.text(0.0, 0.0,"%d points outside" % count_of_points_outside,fontsize=12, transform = pylab.gca().transAxes)

    pylab.draw()
    #pylab.savefig(output_image_path)
    pylab.savefig(output_image_path, dpi=dpi)
    pylab.close()


def plot_one_slice_of_ninja_star_samples_2(samples, output_image_path_generator, dpi=100):

    import ninja_star_distribution

    pylab.hold(True)

    print "Computing the original pdf values."
    M = 4.0
    mesh_x,mesh_y = np.mgrid[-M:M:.01, -M:M:.01]
    z = ninja_star_distribution.mesh_pdf(mesh_x, mesh_y)

    print "Generating the nice plots."
    model_pdf_values_plot_handle = plt.pcolor(mesh_x, mesh_y, z)
    #plt.winter()
    plt.pink()
    #d = plt.colorbar(model_pdf_value_plot_handle, orientation='horizontal')

    for c in np.arange(samples.shape[0]):
        x = samples[c,:,0]
        y = samples[c,:,1]
        scatter_handle = pylab.scatter(x, y)

        pylab.draw()
        pylab.savefig(output_image_path_generator(c), dpi=dpi)
        print "Wrote " + output_image_path_generator(c)                                             
        del(scatter_handle)

    pylab.close()



if __name__ == "__main__":
    main()