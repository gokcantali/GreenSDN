from link import Link

class Port:
	capacity = 10000000	# bytes per second
	packet_size = 100	# bytes	
	base_power = 100
	
	def __init__(self, switch_or_host, number=None):	
		self.capacity = Port.capacity
		self.current_flow = 0
		self.connected_to_port = None
		self.is_active = True
		self.is_connected = False
		self.number = 0

		self.switch_or_host = switch_or_host
		self.switch = None
		self.host = None
		if number == None:	# this is a host port
			self.host = switch_or_host # host
		else:
			self.switch = switch_or_host # switch
			self.number = number

		self.incoming_link = None
		self.outgoing_link = None

	def __str__(self):
		if self.switch != None:
			return 'Port Number: ' + str(self.number) + ' with active status: ' + str(self.is_active) + '\n' \
								   + ', current_flow: ' + str(self.current_flow) + ', belongs to switch: ' + self.switch.identity
		elif self.host != None:
			return 'Port Number: ' + str(self.number) + ' with active status: ' + str(self.is_active) + '\n' \
								   + ', current_flow: ' + str(self.current_flow) + ', belongs to host: ' + self.host.identity

	def deactivate(self):
		self.is_active = False

	def activate(self):
		self.is_active = True

	def connect_to_port(self, port, capacity):
		self.connected_to_port = port
		self.is_connected = True
		port.connected_to_port = self
		port.is_connected = True

		link_capacity = capacity if capacity != None else Link.default_capacity

		self.outgoing_link = port.incoming_link = Link(link_capacity,self,port)
		self.incoming_link = port.outgoing_link = Link(link_capacity,port,self)

	def get_utilization(self):
		return (self.current_flow * Port.packet_size)/self.capacity

	def send_flow(self, flow_rate, source, target, path):
		response = self.outgoing_link.add_flow(flow_rate, source, target, path)
		if response == -1:
			#print 'Flow could not be sent!'
			return 

	def receive_flow(self, flow_rate, source, target, path):
		self.switch_or_host.receive_flow(flow_rate, source, target, path, self)

	def print_link_utilizations(self):
		print 'Incoming link of Port number %s belonging to Switch/Host %s has flow %s' % (self.number, self.switch_or_host.identity, self.incoming_link.get_utilization())
		print 'Outgoing link of Port number %s belonging to Switch/Host %s has flow %s' % (self.number, self.switch_or_host.identity, self.outgoing_link.get_utilization())
