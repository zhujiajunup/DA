__author__ = 'jjzhu'

import numpy as np
import matplotlib.pyplot as plt


def sin_figure():
    x = np.arange(-np.pi, np.pi, 0.01)
    y = np.sin(x)
    plt.plot(x, y, 'g')
    plt.show()


def aa():

    import pylab as pl
    # make an array of random numbers with a gaussian distribution with
    # mean = 5.0
    # rms = 3.0
    # number of points = 1000
    data = np.random.normal(5.0, 3.0, 1000)
    # make a histogram of the data array
    pl.hist(data)
    # make plot labels
    pl.xlabel('data')
    pl.show()

def plot():

    x = [0, 1, 2, 3, 4, 5]
    y = [0.1, 0.2, 0.2, 0.3, 0.2, 0.1]

    plt.plot(x, y, '-.r')

    plt.show()


def main():
    plot()

if __name__ == '__main__':
    main()