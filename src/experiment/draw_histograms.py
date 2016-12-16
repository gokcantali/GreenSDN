import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


def plot(filename):
	file = open(filename, 'r')
	values = list(eval(file.read()).values())

	ser = np.array(values)
	weights = np.ones_like(ser)/len(ser)

	fig, axs = plt.subplots(nrows=2, ncols=1, sharex=True)
	ax = axs[0]

	# plot weighted histogram
	ax.hist(ser, weights=weights, facecolor='blue')
	ax.set_ylabel('Frequency')

	# find minimum and maximum of xticks, so we know
	# where we should compute theoretical distribution
	ax = axs[1]
	xt = plt.xticks()[0]  
	xmin, xmax = min(xt), max(xt)  
	lnspc = np.linspace(xmin, xmax, len(ser))

	ax.hist(ser, normed=True, facecolor='blue') # plot normed histogram

	# lets try the normal distribution
	m, s = stats.norm.fit(ser) # get mean and standard deviation  
	pdf_g = stats.norm.pdf(lnspc, m, s) # now get theoretical values in our interval  
	ax.plot(lnspc, pdf_g, label="Normal") # plot it

	ax.errorbar([200000], [0.00001], xerr=[[30000], [10000]], fmt='--x') # plot our result
	ax.set_ylabel('Density')

	plt.xlabel('Power Consumption (W)')
	plt.legend()
	plt.show()

	print('mean: ' + str(m))
	print('std. dev.: ' + str(s))

plot('k=10_mu=0.2_L=100000000')