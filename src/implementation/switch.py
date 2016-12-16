from port import Port

class Switch:

	base_power = 1183
	port_number = 4 # default

	switch_types = {
		0 : 'Core',
		1 : 'Aggregate',
		2 : 'Edge'
	}

	def __init__(self, type, number):
		self.base_power = Switch.base_power
		if type > len(Switch.switch_types) - 1:
			print 'No such type of switch!'
			return None
		self.port_number = Switch.port_number
		self.switch_type = Switch.switch_types[type]
		self.is_active = True
		self.ports = []
		self.connected_switches = []
		self.connected_hosts = []
		self.identity = Switch.switch_types[type] + '#' + str(number)

		#create ports
		for i in range(0, self.port_number):
			port = Port(self, i)
			self.add_port(port)

	def __str__(self):
		return 'Switch id: ' + self.identity + ' --- active status: ' + str(self.is_active) + '\n' \
							 + 'number of connected switches: ' + str(len(self.connected_switches))

	def add_port(self, port):
		self.ports.append(port)

	def connect_to_host(self, host):
		self.connected_hosts.append(host)
		for source_port in self.ports:
			if not source_port.is_connected:
				source_port.connect_to_port(host.port, None)
				self.connected_hosts.append(host)
				host.connect_to_switch(self)
				return

	def connect_to_switch(self, switch):
		source_port_found = None
		dest_port_found = None
		if switch not in self.connected_switches:
			for source_port in self.ports:
				if not source_port.is_connected:
					source_port_found = source_port 
					for destination_port in switch.ports:
						if not destination_port.is_connected:
							dest_port_found = destination_port
							source_port.connect_to_port(destination_port, None)
							self.connected_switches.append(switch)
							switch.connected_switches.append(self)
							return
		print 'Error connecting switches ', self.identity, ' and ', switch.identity
		print 'source port found', source_port_found
		print 'dest port found', dest_port_found
		print '\n' 

	def deactivate(self):
		self.is_active = False

	def activate(self):
		self.is_active = True

	def send_flow(self, flow_rate, source, target, path, target_port):
		target_port.send_flow(flow_rate, source, target, path)

	def receive_flow(self, flow_rate, source, target, path, source_port):
		#print 'Flow with rate %s came into the Switch: %s from Port: %s' %(flow_rate, self.identity, source_port.number)
		path_splitted = path.split("-")
		if self.identity not in path_splitted:
			print 'Error, Switch %s is not supposed be on the path' % self
			return -1

		index = path_splitted.index(self.identity)
		next_switch_or_host_identity = path_splitted[index+1]

		if 'Host' not in next_switch_or_host_identity:	
			for connected_switch in self.connected_switches:
				if connected_switch.identity == next_switch_or_host_identity:
					for port in self.ports:
						if port.connected_to_port.switch_or_host.identity == next_switch_or_host_identity:
							self.send_flow(flow_rate, source, target, path, port)
							return 0
		else:
			for connected_host in self.connected_hosts:
				if connected_host.identity == next_switch_or_host_identity:
					for port in self.ports:
						if port.connected_to_port.switch_or_host.identity == next_switch_or_host_identity:
							self.send_flow(flow_rate, source, target, path, port)
							return 0
		print 'Could not find the port connecting to the next target: %s' %next_switch_or_host_identity
		return -1

	def print_link_utilizations(self):
		for port in self.ports:
			port.print_link_utilizations()