
class Link:
	default_capacity = 10000000 # 1 Gb by default
	packet_size = 1000	# bits

	def __init__(self, capacity, source, destination):
		self.capacity = capacity if capacity != None else Link.default_capacity
		self.current_flow = 0 # packets per second

		self.source_port = source
		self.destination_port = destination

		self.identity = 'Link from ' + self.source_port.switch_or_host.identity + ' to ' + self.destination_port.switch_or_host.identity

	def __str__(self):
		return self.identity + '\nCarrying flow with rate: ' + str(self.current_flow)

	def get_utilization(self):
		return (float(self.current_flow) * Link.packet_size)/self.capacity

	def add_flow(self, flow_rate, source, target, path):
		if self.current_flow + flow_rate > (self.capacity / Link.packet_size):
			#print 'error! too much flow on the link: ' + self.identity
			return -1

		self.current_flow += flow_rate
		self.destination_port.receive_flow(flow_rate, source, target, path)

		return 0