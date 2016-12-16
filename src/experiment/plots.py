import numpy as np
import matplotlib.pylab as plt
#from scipy import stats

import re

def open_file(k, mu, a):
	return open('k='+str(k)+'_mu='+str(mu)+'_a='+str(a), 'r')

def retrieve_results(file):
	input = file.read()
	max_sa, max_ospf = re.findall(r"Max: (\d+\.\d+)", input)
	avg_sa, avg_ospf = re.findall(r"Avg: (\d+\.\d+)", input)
	min_sa, min_ospf = re.findall(r"Min: (\d+\.\d+)", input)

	return [float(max_sa), float(avg_sa), float(min_sa)], \
		   [float(max_ospf), float(avg_ospf), float(min_ospf)]

def draw_figures():
	k_options      = [10]
	mu_options     = [0.05, 0.10, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
	alpha_options  = [0.55]


	for k in k_options:
		alpha = alpha_options[0]

		our_solution_avg = []
		our_solution_max_error = []
		our_solution_min_error = []

		ospf_avg = []
		ospf_max_error = []
		ospf_min_error = []
		for mu in mu_options:
			file = open_file(k, mu, alpha)
			our_solution, ospf = retrieve_results(file)
			our_solution_avg.append(our_solution[1])
			our_solution_min_error.append(our_solution[1] - our_solution[2])
			our_solution_max_error.append(our_solution[0] - our_solution[1])

			#print our_solution[1] , '-' , our_solution[2] , '=', our_solution[1] - our_solution[2]

			ospf_avg.append(ospf[1])
			ospf_min_error.append(ospf[1] - ospf[2])
			ospf_max_error.append(ospf[0] - ospf[1])

		plt.figure()
		plt.title("Our solution vs OSPF (k=%s, N=%s)" % (k, (k**3)/4))
		plt.xlim([0, 0.55])
		plt.xlabel(r"Communication Density ($\mu$)")
		plt.ylabel("Power Consumption (W)")
		our_plot = plt.errorbar(np.array(mu_options), np.array(our_solution_avg), 
					 yerr=[np.array(our_solution_min_error), np.array(our_solution_max_error)], 
					 fmt='--o', label='Our solution')
		ospf_plot = plt.errorbar(np.array(mu_options), np.array(ospf_avg),
					 yerr=[np.array(ospf_min_error), np.array(ospf_max_error)],
					 fmt='--x', label='OSPF')
		plt.legend(handles=[our_plot, ospf_plot])
		plt.show()


draw_figures()
