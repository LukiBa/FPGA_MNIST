import os

import numpy as np
import json

import NeuralNetwork
from util import read_np_torch, perform_real_quant, init_network_from_weights, evaluate_network, perform_fake_quant, \
    plot_confusion_matrix, evaluate_network_full, quant2float, init_fake_network_from_weights, read_np_keras, \
    init_quant_network_from_weights


def quant_to_int(x, b, f):
    b_ = b - 1
    return np.clip(x / (2 ** f), a_min=2 ** b_, a_max=2 ** b_ - 1)


def _plot_histogram_fc(x, title='FC Weight Distributions'):
    import matplotlib.pyplot as plt

    assert x.ndim == 2

    n = x.shape[1]

    # 20% Above max value
    ax_lim = 1.2 * np.max(np.abs(x))

    nr = int(np.floor(np.sqrt(n)))
    nc = int(np.ceil(n / nr))
    assert nr * nc >= n

    fig, axes = plt.subplots(nrows=nr, ncols=nc, sharex='all', sharey='all', figsize=(8, 6))
    fig.suptitle(title)
    for ix in range(n):
        i = ix // nc
        j = ix % nc
        axes[i, j].hist(x[:, ix].flatten())
        axes[i, j].set_xlim(-ax_lim, ax_lim)
        # axes[i, j].set_title(f'#{ix}')
    fig.show()


def _plot_histogram_array(x: np.ndarray, title="Conv Kernel Plot"):
    import matplotlib.pyplot as plt

    assert x.ndim == 4

    n = x.shape[3]

    # 20% Above max value
    ax_lim = 1.2 * np.max(np.abs(x))

    nr = int(np.floor(np.sqrt(n)))
    nc = int(np.ceil(n / nr))
    assert nr * nc >= n

    fig, axes = plt.subplots(nrows=nr, ncols=nc, sharex='all', sharey='all', figsize=(8, 6))
    fig.suptitle(title)
    for ix in range(n):
        i = ix // nc
        j = ix % nc
        axes[i, j].hist(x[:, :, :, ix].flatten())
        axes[i, j].set_xlim(-ax_lim, ax_lim)
        # axes[i, j].set_title(f'#{ix}')
    fig.show()


def _quant_weight_error_plot(fweights, weights, layer):
    if layer.startswith('cn'):
        _plot_histogram_array(x=fweights[layer] - weights[layer], title=f'Error plot: {layer}')
    elif layer.startswith('fc'):
        _plot_histogram_fc(x=fweights[layer] - weights[layer], title=f'Error plot: {layer}')
    else:
        raise NotImplementedError(f'Expected cnX.k or fcX.w layer id but got: "{layer}"')


def main():
    weights = read_np_keras(target_dtype=np.float32)
    # weights = read_np_torch(ordering="BHWC", target_dtype=np.float32)
    #_plot_histogram_array(weights['cn1.k'])
    #_plot_histogram_array(weights['cn2.k'])

    #_plot_histogram_fc(weights['fc1.w'])
    #_plot_histogram_fc(weights['fc2.w'])

    # Input activation bits and fractions
    ia_b = np.array([8, 8, 8, 8])
    ia_f = np.array([8, 5, 5, 5])

    # Weights bits and fractions
    w_b = np.array([4, 4, 4, 4])
    w_f = np.array([4, 4, 4, 4])

    # Output activation bits and fractions
    oa_b = np.array([8, 8, 8, 8])
    oa_f = np.array([5, 5, 5, 5])

    # Should perform well
    qweights, shift, options = perform_real_quant(weights,
                                                  in_bits=ia_b, in_frac=ia_f,
                                                  w_bits=w_b, w_frac=w_f,
                                                  out_bits=oa_b, out_frac=oa_f)
    fweights = quant2float(qweights, options)
    # fweights = perform_fake_quant(weights, target_bits=8, frac_bits=4)

    # Check if it has worked
    our_net = init_network_from_weights(weights, from_torch=False)
    fake_net = init_fake_network_from_weights(qweights=fweights, shift=shift, options=options)
    quant_net = init_quant_network_from_weights(qweights=qweights, shift=shift, options=options)

    mnist = NeuralNetwork.Reader.MNIST(folder_path='/tmp/mnist/')
    test_images = mnist.test_images()
    test_labels = mnist.test_labels()
    batch_size = 50

    # Check network performance (might take some time)
    # Accuracy should be at least 90% even with quantization

    # ---- Evaluate Real Quant  ----
    qaccuracy, qcm = evaluate_network_full(batch_size, quant_net, test_images, test_labels, images_as_int=True)
    print("Quantised Network:   ", qaccuracy)

    # ---- Evaluate Normal ----
    accuracy, cm = evaluate_network_full(batch_size, our_net, test_images, test_labels)
    print("Network:             ", accuracy)

    # ---- Evaluate Fake Quant  ----
    # fqaccuracy, fqcm = evaluate_network_full(batch_size, fake_net, test_images, test_labels)
    # print("Quantised Network:   ", qaccuracy)

    classnames = list(map(str, range(10)))
    plot_confusion_matrix(cm, title='Confusion matrix (full precision)',
                          target_names=classnames, filename='images/cm')
    plot_confusion_matrix(qcm, title='Confusion matrix (fake fixed point 8/4)',
                          target_names=classnames, filename='images/qcm')

    save_weights(fweights, qweights, weights, config=options)


def prepare_config(config):
    """
    Prepares a dictionary to be stored as a json.
    Converts all numpy arrays to regular arrays
    Args:
        config: The config with numpy arrays

    Returns:
        The numpy free config
    """
    c = {}
    for key, value in config.items():
        if isinstance(value, np.ndarray):
            value = value.tolist()
        c[key] = value
    return c


def save_weights(fweights, qweights, weights, config):
    """
    Saves the weights in numpy and text format. Also stores a config.json file
    Args:
        fweights:
        qweights:
        weights:
        config:

    Returns:

    """

    config = prepare_config(config)

    for key, value in qweights.items():
        dirname = os.path.join('final_weights', 'fpi')
        os.makedirs(dirname, exist_ok=True)
        filename = os.path.join(dirname, key)
        x_ = value.flatten()

        with open(os.path.join(dirname, 'config.json'), 'w') as fp:
            json.dump(config, fp)

        np.savetxt(fname=filename + '.txt', X=x_, fmt='%i', header=str(value.shape))
        np.save(file=filename, arr=value)
    for key, value in fweights.items():
        dirname = os.path.join('final_weights', 'fake_quant')
        os.makedirs(dirname, exist_ok=True)
        filename = os.path.join(dirname, key)
        x_ = value.flatten()
        with open(os.path.join(dirname, 'config.json'), 'w') as fp:
            json.dump(config, fp)

        np.savetxt(fname=filename + '.txt', X=x_, header=str(value.shape))
        np.save(file=filename, arr=value)
    for key, value in weights.items():
        dirname = os.path.join('final_weights', 'float')
        os.makedirs(dirname, exist_ok=True)
        filename = os.path.join(dirname, key)
        x_ = value.flatten()

        np.savetxt(fname=filename + '.txt', X=x_, header=str(value.shape))
        np.save(file=filename, arr=value)


if __name__ == '__main__':
    main()
