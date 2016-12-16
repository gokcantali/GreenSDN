from topology import Topology
from host import Host
from link import Link

import math, random, re

def generate_communication_pairs(topology, density):
	pair_list = []
	number_hosts = len(topology.host_list)
	for source_host in topology.host_list:
		for target_host in topology.host_list:
			if target_host != source_host and random.random() < density:
				pair_list.append((source_host, target_host))
	return pair_list

def generate_traffic_requirement_matrix(topology, pair_list, min_flow, range):
	host_list = topology.host_list
	traffic_requirement_matrix = [[0 for target in host_list] for source in host_list]
	for pair in pair_list:
		source_index = int(pair[0].identity.split("#")[1])
		target_index = int(pair[1].identity.split("#")[1])
		flow = int(min_flow + range * random.random())
		traffic_requirement_matrix[source_index][target_index] = flow
	return traffic_requirement_matrix

def find_path(topology, source, destination, flow):
	def is_aggregation(switch): return 'Aggregate' in switch.identity
	def is_core(switch): return 'Core' in switch.identity
	def is_edge(switch): return 'Edge' in switch.identity

	k = topology.number_of_ports_in_switches
	
	source_index = int(source.identity.split("#")[1])
	source_pod = int(source_index / ((k/2)**2))
	source_edge_index = int((source_index % ((k/2)**2)) / (k/2))

	target_index = int(destination.identity.split("#")[1])
	target_pod = int(target_index / ((k/2)**2))
	target_edge_index = int((target_index % ((k/2)**2)) / (k/2))

	result_list = []

	source_edge_switch = source.port.outgoing_link.destination_port.switch
	if not source_edge_switch.is_active or source.port.outgoing_link.get_utilization() + (flow*Link.packet_size)/source.port.outgoing_link.capacity > 1:
		#print 'The edge connecting source is not active or not enough link capacity!'
		return -1

	# if target is connected to the same edge switch which source is connected to
	if source_pod == target_pod and source_edge_index == target_edge_index:
		flow_path = source.identity + '-' + source_edge_switch.identity + '-' + destination.identity
		result_list.append(flow_path)

	# if target is in the same pod as the source
	if source_pod == target_pod and source_edge_index != target_edge_index:
		source_aggregation_switches = filter(is_aggregation, source_edge_switch.connected_switches)
		for aggregation_switch in source_aggregation_switches:
			if not aggregation_switch.is_active:
				continue
			else:
				link = aggregation_switch.ports[(k/2)+target_edge_index].incoming_link
				if (link.current_flow + flow)*Link.packet_size/link.capacity > 1:
					#print 'Not enough link capacity on link %s' % link
					continue
			target_edge_switch = filter(is_edge, aggregation_switch.connected_switches)[target_edge_index]
			if not target_edge_switch.is_active or destination.port.incoming_link.get_utilization() + (flow*Link.packet_size)/destination.port.incoming_link.capacity > 1:
				#print 'The edge connecting target is not active or not enough link capacity!'
				return -1
			flow_path = source.identity + '-' + source_edge_switch.identity + '-' + \
						aggregation_switch.identity + '-' + target_edge_switch.identity + '-' + destination.identity
			result_list.append(flow_path)

	source_aggregation_switches = filter(is_aggregation, source_edge_switch.connected_switches)
	for aggregation_switch in source_aggregation_switches:
		if not aggregation_switch.is_active:
			continue
		else:
			link = aggregation_switch.ports[(k/2)+target_edge_index].incoming_link
			if (link.current_flow + flow)*Link.packet_size/link.capacity > 1:
				#print 'Not enough link capacity on link %s' % link
				continue
		core_switches = filter(is_core, aggregation_switch.connected_switches)
		for core_switch in core_switches:
			if not core_switch.is_active:
				continue
			else:
				link = core_switch.ports[source_pod].incoming_link
				if (link.current_flow + flow)*Link.packet_size/link.capacity > 1:
					#print 'Not enough link capacity on link %s' % link
					continue
			target_index = int(destination.identity.split("#")[1])
			pod = int(target_index / ((k/2)**2))
			target_aggregation_switch = core_switch.connected_switches[pod]
			if not target_aggregation_switch.is_active or aggregation_switch == target_aggregation_switch:
				continue
			else:
				link = core_switch.ports[target_pod].outgoing_link
				if (link.current_flow + flow)*Link.packet_size/link.capacity > 1:
					#print 'Not enough link capacity on link %s' % link
					continue
			edge_index = int((target_index % ((k/2)**2)) / (k/2))
			edges_of_pod = filter(is_edge, target_aggregation_switch.connected_switches)
			target_edge_switch = edges_of_pod[edge_index]
			if not target_edge_switch.is_active or source_edge_switch == target_edge_switch or destination.port.incoming_link.get_utilization() + (flow*Link.packet_size)/destination.port.incoming_link.capacity > 1:
				#print 'The edge connecting target is not active or not enough link capacity!'
				return -1
			flow_path = source.identity + '-' + source_edge_switch.identity + '-' + \
					    aggregation_switch.identity + '-' + core_switch.identity + '-' + \
					    target_aggregation_switch.identity + '-' + target_edge_switch.identity + \
					    '-' + destination.identity

			result_list.append(flow_path)
	return result_list if len(result_list) > 0 else -1

def get_flow_options(topology, trm):
	flow_options = {}
	for i in range(len(trm)):
		for j in range(len(trm[i])):
			if trm[i][j] != 0:
				source = topology.host_list[i]
				target = topology.host_list[j]
				flow_options[(source.identity,target.identity)] = find_path(topology, source, target, trm[i][j])
	return flow_options

def get_flow_options_for_pair(topology, source, target, flow_rate):
	return find_path(topology, source, target, flow_rate)

def initiate_flows(topology, trm, flow_options):
	topology.remove_flows()
	chosen_paths = []
	for i in range(len(trm)):
		for j in range(len(trm[i])):
			if trm[i][j] != 0:
				source = topology.host_list[i]
				target = topology.host_list[j]
				if flow_options[(source.identity,target.identity)] != -1 and flow_options[(source.identity,target.identity)] != []:
					random_flow_path = random.choice(flow_options[(source.identity,target.identity)])
					source.send_flow(trm[i][j], source, target, random_flow_path)
					chosen_paths.append(random_flow_path)
	return chosen_paths

def initiate_flows_2(topology, trm):
	topology.remove_flows()
	chosen_paths = []
	for i in range(len(trm)):
		for j in range(len(trm[i])):
			if trm[i][j] != 0:
				source = topology.host_list[i]
				target = topology.host_list[j]
				flow_options = get_flow_options_for_pair(topology, source, target, trm[i][j])
				if len(flow_options) == 0:
					print 'nooo!!'
				else:
					random_flow_path = random.choice(flow_options)
					source.send_flow(trm[i][j], source, target, random_flow_path)
					chosen_paths.append(random_flow_path)
	return chosen_paths

def initiate_flows_manually(topology, trm, chosen_paths):
	topology.remove_flows()
	for path in chosen_paths:
		source_index, target_index = map(lambda x: int(x), re.findall('Host#(\d+)', path))
		source = topology.host_list[source_index]
		target = topology.host_list[target_index]
		source.send_flow(trm[source_index][target_index], source, target, path)
	return 1

def is_there_path_for_all(flow_options):
	for val in flow_options.values():
		if val == -1:
			return False
	return True

def main():
	topology = Topology(4)
	topology.create_topology()
	pairs = generate_communication_pairs(topology, 0.01)
	for pair in pairs:
		print pair[0].identity + '->' + pair[1].identity

	trm = generate_traffic_requirement_matrix(topology, pairs, 1000, 2000)
	initiate_flows(topology, trm, get_flow_options(topology, trm))
	topology.print_link_utilizations()
	return topology

if __name__ == '__main__':
	main()