def reader(data, params, **kwargs):
    print("reader")
    # do some modify
    return data


def process(data, params, **kwargs):
    print("process")
    # do some modify
    return data


def extract(data, params, **kwargs):
    print("feature")
    # do some modify
    return data


def visualization(data, params, **kwargs):
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
