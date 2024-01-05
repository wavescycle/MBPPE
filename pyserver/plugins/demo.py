def reader(data, params, info):
    print("reader")
    # do some modify
    return data


def process(data, params, info):
    print("process")
    # do some modify
    return data


def extract(data, params, info):
    print("feature")
    # do some modify
    return data


def visualization(data, params, info):
    import matplotlib.pyplot as plt
    import numpy as np

    # Create a range of values
    x = np.linspace(0, 10, 100)

    # Create a simple function of x
    y = np.sin(x)

    # Create a new figure
    plt.figure()

    # Plot x against y
    plt.plot(x, y)

    return plt
