# import numpy as np
# from scipy.ndimage import map_coordinates
# import matplotlib.pyplot as plt


# def plot_flux_slice(data, model, residual, y_slice, xlim1, xlim2):
#     x0 = np.arange(data.shape[1])
#     x = x0 - 1    # imfit --> numpy 
#     coords = np.vstack([np.full_like(x, y_slice, dtype = float), x])

#     data_slice = map_coordinates(data, coords, order = 1)
#     model_slice = map_coordinates(model, coords, order = 1)
#     residual_slice = map_coordinates(residual, coords, order = 1)

#     # we use x0 for plotting because we are not using numpy
#     fig, ax = plt.subplots(1, 2, figsize = (12, 4))
#     ax[0].plot(x0, data_slice, label = 'Data')
#     ax[0].plot(x0, model_slice, label = 'Model')
#     ax[0].set_ylabel('Flux')
#     ax[0].set_xlabel('x[pixels]')
#     ax[0].set_xlim(xlim1, xlim2)

#     ax[1].plot(x0, residual_slice, label = 'Residual')
#     ax[1].axhline(0, ls = '--', lw=1)
#     ax[1].set_ylabel('Flux')
#     ax[1].set_xlabel('x[pixels]')
#     ax[1].set_xlim(xlim1, xlim2)
#     plt.show()

import numpy as np
from scipy.ndimage import map_coordinates
import matplotlib.pyplot as plt


def plot_flux_slice(data, model, residual, y_slice, xlim1, xlim2):
    x0 = np.arange(data.shape[1])
    x = x0 - 1    # imfit --> numpy 
    coords = np.vstack([np.full_like(x, y_slice, dtype = float), x])

    data_slice = map_coordinates(data, coords, order = 1)
    model_slice = map_coordinates(model, coords, order = 1)
    residual_slice = map_coordinates(residual, coords, order = 1)

    plt.plot(x0, data_slice, label = 'Data')
    plt.plot(x0, model_slice, label = 'Model')
    plt.plot(x0, residual_slice, label = 'Residual')
    plt.axhline(0, ls = '--', lw=1)
    plt.ylabel('Flux')
    plt.xlabel('x [pixels]')
    plt.legend()
    plt.xlim(xlim1, xlim2)

    plt.show()

