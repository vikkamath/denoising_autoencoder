
import subprocess
import cPickle

# pseudo-parameter
dir = "/data/lisatmp2/alaingui/dae/dae_trained_models/gaussian_mixture_d10/experiment_02"
#dir = "/data/lisatmp2/alaingui/dae/dae_trained_models/gaussian_mixture_d100/experiment_01"

list_abs_path_files = [e for e in subprocess.check_output("find %s -name extra_details.pkl" % (dir,), shell=True).split("\n") if len(e)>0]


list_contents = [cPickle.load(open(f)) for f in list_abs_path_files]


[e for e in list_contents if (e['maxiter'] == 1000) and (e['act_func'] == ['tanh', 'tanh'])]