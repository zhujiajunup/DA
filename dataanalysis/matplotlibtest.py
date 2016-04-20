__author__ = 'jjzhu'

import numpy as np
import matplotlib.pyplot as plt


def horizontal_bar():
    """
    Simple demo of a horizontal bar chart.
    """
    plt.rcdefaults()

    # Example data
    people = ('Tom', 'Dick', 'Harry', 'Slim', 'Jim')
    y_pos = np.arange(len(people))
    performance = 3 + 10 * np.random.rand(len(people))
    error = np.random.rand(len(people))

    plt.barh(y_pos, performance, xerr=error, align='center')
    plt.yticks(y_pos, people)
    plt.xlabel('Performance')
    plt.title('How fast do you want to go today?')
    plt.show()


def fill():
    """
    Simple demo of the fill function.
    """

    x = np.linspace(0, 1, 500)
    y = np.sin(4 * np.pi * x) * np.exp(-5 * x)

    plt.fill(x, y)
    plt.grid(True)
    plt.show()

def scatter():
    """
    Simple demo of a scatter plot.
    """
    N = 50
    x = np.random.rand(N)
    y = np.random.rand(N)
    colors = np.random.rand(N)
    area = np.pi * (15 * np.random.rand(N))**2  # 0 to 15 point radiuses

    plt.scatter(x, y, s=area, c=colors, alpha=0.5)
    plt.show()


def main():
    scatter()

if __name__ == '__main__':
    main()