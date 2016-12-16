from traffic import *
from math import exp
import random
import os
import datetime

from port import Port
from switch import Switch

def calculate_power(topology):
	total_power = 0.0

	base_switch_pw = Switch.base_power
	base_port_pw = Port.base_power

	all_switches = []
	all_switches.extend(topology.core_switch_list)
	all_switches.extend(topology.aggregate_switch_list)
	all_switches.extend(topology.edge_switch_list)
	for switch in all_switches:
		if not switch.is_active:
			continue
		total_power += base_switch_pw
		for port in switch.ports:
			average_utilization = 0.5*port.outgoing_link.get_utilization() + 0.5*port.incoming_link.get_utilization()
			total_power += base_port_pw * average_utilization
	return total_power

def ospf(topology, trm):
	topology.remove_flows()
	#first all switches are active
	for switch in topology.get_all_switches():
		switch.activate()

	chosen_paths = []
	flow_options = get_flow_options(topology, trm)
	for i in range(len(trm)):
		for j in range(len(trm[i])):
			if trm[i][j] != 0:
				source = topology.host_list[i]
				target = topology.host_list[j]
				#possible_flows = flow_options[(source.identity,target.identity)]
				possible_flows = get_flow_options_for_pair(topology, source, target, trm[i][j])
				if possible_flows != -1 and len(possible_flows) != 0:
					if len(possible_flows) == 1:
						source.send_flow(trm[i][j], source, target, possible_flows[0])
						chosen_paths.append(possible_flows[0])
					else:
						min_hop_number = 9999
						shortest_path = ''
						for possible_flow in possible_flows:
							hop_number = possible_flow.count('-')
							if hop_number < min_hop_number:
								min_hop_number = hop_number
								shortest_path = possible_flow
						source.send_flow(trm[i][j], source, target, shortest_path)
						chosen_paths.append(shortest_path)

	all_paths = ','.join(chosen_paths)

	open_switches = []
	# turn off unused switches
	for switch in topology.get_all_switches():
		if switch.identity not in all_paths:
			switch.deactivate()
		else:
			open_switches.append(switch)

	return calculate_power(topology), chosen_paths, open_switches

def acceptance_probability(energy, new_energy, temperature):
	if new_energy < energy:
		return 1.0

	return exp((energy - new_energy) / temperature)

def simulated_annealing(topology, trm, initial_temperature, cooling_rate, probability_toggle_switch):
	def is_active(switch): return switch.is_active
	def is_inactive(switch): return not switch.is_active

	open_switches = []
	temperature = initial_temperature

	# all_switches = []
	# all_switches.extend(topology.core_switch_list)
	# all_switches.extend(topology.aggregate_switch_list)
	# all_switches.extend(topology.edge_switch_list)

	# initial solution
	for switch in topology.get_all_switches():
		if random.random() < 0.5:
			switch.deactivate()

	flow_options = get_flow_options(topology, trm)
	while not is_there_path_for_all(flow_options):
		random.choice(filter(is_inactive, topology.get_all_switches())).activate()
		flow_options = get_flow_options(topology, trm)

	best_solution = initiate_flows(topology, trm, flow_options)
	best_energy = calculate_power(topology)
	open_switches = filter(is_active, topology.get_all_switches())

	while temperature > 100:
		switch = None
		if random.random() < probability_toggle_switch:
			switch = random.choice(topology.get_all_switches())
			if switch.is_active:
				switch.deactivate()
			else:
				switch.activate()
			flow_options = get_flow_options(topology, trm)
			# while not is_there_path_for_all(flow_options):
			# 	random.choice(filter(is_inactive, topology.get_all_switches())).activate()
			# 	flow_options = get_flow_options(topology, trm)
			if not is_there_path_for_all(flow_options):
				switch.activate()
				initiate_flows_manually(topology, trm, best_solution)
				continue
		
		flow_options = get_flow_options(topology, trm)
		solution = initiate_flows(topology, trm, flow_options)
		energy = calculate_power(topology)

		if energy < best_energy:
			best_energy = energy
			best_solution = solution
			open_switches = filter(is_active, topology.get_all_switches())
			#print 'found a better solution! ', best_energy

		elif random.random() < acceptance_probability(best_energy, energy, temperature):
			best_energy = energy
			best_solution = solution
			open_switches = filter(is_active, topology.get_all_switches())
			#print 'found worse but accepted! ', best_energy

		else:
			if switch != None:
				if switch.is_active:
					switch.deactivate()
				else:
					switch.activate()
			initiate_flows_manually(topology, trm, best_solution)

		temperature = (1-cooling_rate)*temperature

	#print 'best energy: ', best_energy
	return best_energy, best_solution, open_switches

def setup_parameters(port_number, communication_density, min_flow, max_flow, 
					 initial_temperature, cooling_rate, probability_toggle_switch):
	topology = Topology(port_number)
	topology.create_topology()
	pairs = generate_communication_pairs(topology, communication_density)
	trm = generate_traffic_requirement_matrix(topology, pairs, min_flow, max_flow)
	
	simulation_start = datetime.datetime.now()
	simulated_annealing_results = simulated_annealing(topology, trm, initial_temperature, cooling_rate, probability_toggle_switch)
	simulation_end = datetime.datetime.now()
	simulation_time = (simulation_end-simulation_start)

	ospf_results = ospf(topology, trm)
	return [simulated_annealing_results, ospf_results, simulation_time]

def experiments_phase_1(number_of_repetitions, k_options, mu_options, 
						T_options, Tfinal_options, alpha_options, beta_options):
	for r in range(1, number_of_repetitions+1):
		for k in k_options:
			for mu in mu_options:
				for T in T_options:
					for Tfinal in Tfinal_options:
						for alpha in alpha_options:
							for beta in beta_options:
								file_name = 'k='+str(k)+'_mu='+str(mu)+'_T='+str(T)+'_Tfinal='+str(Tfinal)\
											+'_a='+str(alpha)+'_b='+str(beta)+'_r='+str(r)
								file_path = '..'+os.sep+'experiment_results'+os.sep+file_name
								file = open(file_path, 'w')
								results = setup_parameters(k,mu,1000,2000,T,alpha,beta)

								file.write('---Simulated Annealing---')
								best_energy, best_solution, open_switches = results[0]
								file.write('\nbest_energy: ' + str(best_energy))
								#file.write('\nbest_solution: ' + str(best_solution))
								file.write('\n# of open_switches: ' + str(len(open_switches)))

								file.write('\n\n---OSPF---')
								best_energy, best_solution, open_switches = results[1]
								file.write('\nbest_energy: ' + str(best_energy))
								#file.write('best_solution: ' + str(best_solution))
								file.write('\n# of open_switches: ' + str(len(open_switches)))

								file.write('\n\n---Simulation Time---')
								file.write('\nMinutes: ' + str(results[2].seconds // 60 % 60))
								file.write('\nSeconds: ' + str(results[2].seconds % 60))
								file.close()

def experiments_phase_2(number_of_repetitions, k_options, 
						mu_options, alpha_options):
	for k in k_options:
		for mu in mu_options: 
			for alpha in alpha_options:
				for r in range(1, number_of_repetitions+1):
					file_name = 'k='+str(k)+'_mu='+str(mu)\
								+'_a='+str(alpha)+'_r='+str(r)
					file_path = '..'+os.sep+'experiment_results_phase2'+os.sep+file_name
					file = open(file_path, 'w')
					results = setup_parameters(k,mu,1000,2000,10000,alpha,0.90)

					file.write('---Simulated Annealing---')
					best_energy, best_solution, open_switches = results[0]
					file.write('\nbest_energy: ' + str(best_energy))
					#file.write('\nbest_solution: ' + str(best_solution))
					file.write('\n# of open_switches: ' + str(len(open_switches)))

					file.write('\n\n---OSPF---')
					best_energy, best_solution, open_switches = results[1]
					file.write('\nbest_energy: ' + str(best_energy))
					#file.write('best_solution: ' + str(best_solution))
					file.write('\n# of open_switches: ' + str(len(open_switches)))

					file.write('\n\n---Simulation Time---')
					file.write('\nMinutes: ' + str(results[2].seconds // 60 % 60))
					file.write('\nSeconds: ' + str(results[2].seconds % 60))
					file.close()

def statistical_quality_measure(k, mu, L):
	Link.default_capacity = L

	topology = Topology(k)
	topology.create_topology()
	
	pairs = generate_communication_pairs(topology, mu)
	trm = generate_traffic_requirement_matrix(topology, pairs, 1000, 2000)

	hist = {}
	for i in range(10000):
		# each iteration is a solution (but it might be INFEASIBLE!)

		topology.remove_flows()
		for switch in topology.get_all_switches():
			switch.activate()

		prob = random.random()
		number_of_open_switches = len(topology.get_all_switches())
		for switch in topology.get_all_switches():
			on_or_off = random.random()
			if on_or_off < prob:
				switch.deactivate()
				number_of_open_switches -= 1

		chosen_paths = []
		no_solution = False
		num_flows = 0
		for i in range(len(trm)):
			for j in range(len(trm[i])):
				if trm[i][j] != 0:
					num_flows += 1
					source = topology.host_list[i]
					target = topology.host_list[j]
					#possible_flows = flow_options[(source.identity,target.identity)]
					possible_flows = get_flow_options_for_pair(topology, source, target, trm[i][j])
					if possible_flows != -1 and len(possible_flows) != 0:
						if len(possible_flows) == 1:
							source.send_flow(trm[i][j], source, target, possible_flows[0])
							chosen_paths.append(possible_flows[0])
						else:
							random_flow_path = random.choice(possible_flows)
							source.send_flow(trm[i][j], source, target, random_flow_path)
							chosen_paths.append(random_flow_path)
					else:
						no_solution = True
						break
			if no_solution:
				break
		if no_solution:
			continue

		chosen_paths.sort()
		hist_key = 'N_' + str(number_of_open_switches) + "_" + "_".join(chosen_paths)
		if hist_key not in hist:
			hist[hist_key] = calculate_power(topology)
			# if hist[hist_key] > 26000:
			# 	print 'num flows: ' + str(num_flows)
			# 	print 'num open switches: ' + str(number_of_open_switches)
			# 	return hist, chosen_paths

	file_path = '..'+os.sep+'statistical_quality_measurement'+os.sep+'k='+str(k)+'_mu='+str(mu)+'_L='+str(L)
	file = open(file_path, 'w')
	file.write(str(hist))
	file.close()

	return hist

def stat_qual_meas(k, mu, L):
	Link.default_capacity = L

	topology = Topology(k)
	topology.create_topology()
	
	pairs = generate_communication_pairs(topology, mu)
	trm = generate_traffic_requirement_matrix(topology, pairs, 1000, 2000)

	hist = {}

	all_switches = topology.get_all_switches()
	num_switches = len(all_switches)
	for i in range(2**num_switches):
		for j in range(num_switches):
			if bin(i & j) == bin(0):
				all_switches[j].deactivate()
			else:
				all_switches[j].activate()

		#chosen_paths = []
		no_solution = False
		for i in range(len(trm)):
			for j in range(len(trm[i])):
				if trm[i][j] != 0:
					source = topology.host_list[i]
					target = topology.host_list[j]
					#possible_flows = flow_options[(source.identity,target.identity)]
					possible_flows = get_flow_options_for_pair(topology, source, target, trm[i][j])
					if possible_flows != -1 and len(possible_flows) != 0:
						if len(possible_flows) == 1:
							source.send_flow(trm[i][j], source, target, possible_flows[0])
							#chosen_paths.append(possible_flows[0])
						else:
							random_flow_path = random.choice(possible_flows)
							source.send_flow(trm[i][j], source, target, random_flow_path)
							#chosen_paths.append(random_flow_path)
					else:
						no_solution = True
						break
			if no_solution:
				break
		if not no_solution:
			hist[i].append(calculate_power(topology))

	return hist


def begin_simulation():
	# k_options      = [4, 6]
	# #n_options     = [16, 54]
	# mu_options     = [0.05, 0.20]
	# T_options      = [5000, 10000]
	# Tfinal_options = [100, 1000]
	# alpha_options  = [0.01, 0.05]
	# beta_options   = [0.75, 0.90]
	# repetitions    = 1

	# experiments_phase_1(repetitions, k_options, mu_options, 
	# 					T_options, Tfinal_options, alpha_options, beta_options)

	k_options      = [4, 6, 8, 10, 12]
	#n_options     = [16, 54]
	mu_options     = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
	alpha_options  = [0.95, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.05]
	repetitions    = 10

	experiments_phase_2(repetitions, k_options, mu_options, alpha_options)

if __name__ == '__main__':
	# results = setup_parameters(8, 0.10, 1000, 2000, 10000, 0.02, 0.95)
	
	# print '---Simulated Annealing---\n'
	# best_energy, best_solution, open_switches = results[0]
	# print 'best_energy', best_energy
	# print 'best_solution', best_solution
	# print 'open_switches', open_switches

	# print '---OSPF---\n'
	# best_energy, best_solution, open_switches = results[1]
	# print 'best_energy', best_energy
	# print 'best_solution', best_solution
	# print 'open_switches', open_switches

	#begin_simulation()

	# k_options      = [4, 6]
	# L_options      = [10000000, 1000000000]
	# mu_options     = [0.5, 0.20]

	# for k in k_options:
	# 	for mu in mu_options:
	# 		for L in L_options:
	# 			statistical_quality_measure(k, mu, L)

	statistical_quality_measure(10, 0.20, 100000000)






