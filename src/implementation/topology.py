from switch import Switch
from host import Host

class Topology:

	def __init__(self, port_number):
		self.number_of_ports_in_switches = port_number
		Switch.port_number = port_number

		self.number_core_switches      = (port_number * port_number) / 4 
		self.number_aggregate_switches = self.number_core_switches * 2
		self.number_edge_switches      = self.number_core_switches * 2
		self.number_hosts              = self.number_edge_switches * (port_number / 2)

		self.core_switch_list       = []
		self.aggregate_switch_list  = []
		self.edge_switch_list       = []
		self.host_list              = []

	def create_topology(self):

		#create core layer switches
		for i in range(0, self.number_core_switches):
			switch = Switch(0, i)
			self.core_switch_list.append(switch)

		#create aggregate layer switches
		for i in range(0, self.number_aggregate_switches):
			switch = Switch(1, i)
			self.aggregate_switch_list.append(switch)

		#create edge layer switches
		for i in range(0, self.number_edge_switches):
			switch = Switch(2, i)
			self.edge_switch_list.append(switch)

		#create hosts
		for i in range(0, self.number_hosts):
			host = Host(i)
			self.host_list.append(host)

		self.connect_switches()
	
	def connect_switches(self):
		pod_number = self.number_of_ports_in_switches # the same as port number
		core_number = pod_number / 2

		#connect core layer to aggregate layer
		for i in range(0, self.number_core_switches):
			core_switch = self.core_switch_list[i]
			connect_index = int(i / core_number)
			for j in range(0, pod_number):
				aggregate_switch = self.aggregate_switch_list[connect_index + j * core_number]
				core_switch.connect_to_switch(aggregate_switch)

		#connect aggregate layer to edge layer
		for i in range(0, self.number_aggregate_switches):
			aggregate_switch = self.aggregate_switch_list[i]
			connect_index = int(i / core_number)
			for j in range(0, core_number):
				edge_switch = self.edge_switch_list[connect_index * core_number + j]
				aggregate_switch.connect_to_switch(edge_switch)

		#connect edge layer to hosts
		for i in range(0, self.number_edge_switches):
			edge_switch = self.edge_switch_list[i]
			for j in range(0, core_number):
				host = self.host_list[i * core_number + j]
				edge_switch.connect_to_host(host)

	def get_all_switches(self):
		all_switches = []
		all_switches.extend(self.core_switch_list)
		all_switches.extend(self.aggregate_switch_list)
		all_switches.extend(self.edge_switch_list)
		return all_switches

	def remove_flows(self):
		all_switches = []
		all_switches.extend(self.core_switch_list)
		all_switches.extend(self.aggregate_switch_list)
		all_switches.extend(self.edge_switch_list)

		for switch in all_switches:
			for port in switch.ports:
				port.outgoing_link.current_flow = 0
				port.incoming_link.current_flow = 0

		for host in self.host_list:
			host.port.outgoing_link.current_flow = 0
			host.port.incoming_link.current_flow = 0

	def print_link_utilizations(self):
		print '---Edge switches---'
		for edge_switch in self.edge_switch_list:
			print edge_switch.print_link_utilizations()
		print '---Aggregate switches---'
		for aggregate_switch in self.aggregate_switch_list:
			print aggregate_switch.print_link_utilizations()
		print '---Core switches---'
		for core_switch in self.core_switch_list:
			print core_switch.print_link_utilizations()

if __name__ == '__main__':
	print 'Hey There!'
	example = Topology(6)
	example.create_topology()

