import os, re

def process_results():
	k_options      = [10]
	mu_options     = [0.05, 0.10, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
	alpha_options  = [0.55]
	repetition_num = 10

	for k in k_options:
		for mu in mu_options:
			for alpha in alpha_options:
				our_solutions  = []
				ospf_solutions = []

				for r in range(1, repetition_num + 1):
					file_name = 'k='+str(k)+'_mu='+str(mu)+'_a='+str(alpha)+'_r='+str(r)
					#print file_name
					output = open(file_name, 'r').read()
					results = re.findall(r"best_energy: (\d+\.\d+)", output)
					our_solutions.append(float(results[0]))
					ospf_solutions.append(float(results[1]))

				min_our_result = min(our_solutions)
				max_our_result = max(our_solutions)
				avg_our_result = sum(our_solutions)/len(our_solutions)

				min_ospf_result = min(ospf_solutions)
				max_ospf_result = max(ospf_solutions)
				avg_ospf_result = sum(ospf_solutions)/len(ospf_solutions)

				result_file_name = 'processed_results'+os.sep+'k='+str(k)+'_mu='+str(mu)+'_a='+str(alpha)

				result_file = open(result_file_name, 'w')
				result_file.write('---Our Solution---\n')
				result_file.write('Max: ' + str(max_our_result) + '\n')
				result_file.write('Avg: ' + str(avg_our_result) + '\n')
				result_file.write('Min: ' + str(min_our_result) + '\n')

				result_file.write('\n---OSPF---\n')
				result_file.write('Max: ' + str(max_ospf_result) + '\n')
				result_file.write('Avg: ' + str(avg_ospf_result) + '\n')
				result_file.write('Min: ' + str(min_ospf_result) + '\n')

				result_file.close()

process_results()