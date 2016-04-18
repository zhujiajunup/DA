__author__ = 'jjzhu'

import numpy as np
import matplotlib.pyplot as plt


def sin_figure():
    x = np.arange(-np.pi, np.pi, 0.01)
    y = np.sin(x)
    plt.plot(x, y, 'g')
    plt.show()


def plot():

    x = [0, 1, 2, 3, 4, 5]
    y = [0.1, 0.2, 0.2, 0.3, 0.2, 0.1]

    plt.plot(x, y, '-.r')

    plt.show()
    plt.save("d:\\1.png")


def main():
    plot()

if __name__ == '__main__':
    main()