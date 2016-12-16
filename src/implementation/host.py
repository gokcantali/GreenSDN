from port import Port
from link import Link

class Host:
	packet_size = 1000 # bits
	
	def __init__(self, number):
		self.identity = 'Host#' + str(number)
		self.connected_to_switch = None
		self.port = Port(self,None)

	def __str__(self):
		return 'Host id: ' + self.identity

	def connect_to_switch(self, switch):
		self.connected_to_switch = switch

	def send_flow(self, flow_rate, source, target, path):
		return self.port.send_flow(flow_rate, source, target, path)

	def receive_flow(self, flow_rate, source, target, path, port):
		if target.identity == self.identity:
			#print '%s received flow with rate %s (p/s) from %s' % (self.identity, flow_rate, source.identity)
			pass
		else:
			print 'This flow is not intended for me!'
			return -1


