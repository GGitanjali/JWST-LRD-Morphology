from astropy.io import fits
from astropy.stats import sigma_clipped_stats
import numpy as np


def data_info(filename):

    data = fits.getdata(filename).astype(float)

    mean, median, std = sigma_clipped_stats(data, sigma=3, maxiters=10)

    y_peak, x_peak = np.unravel_index(np.nanargmax(data), data.shape)

    print("File:", filename)
    print("Shape:", data.shape)
    print("Min:", np.nanmin(data))
    print("Max:", np.nanmax(data))
    print("Sky median:", median)
    print("Sky RMS:", std)
    print("Peak numpy x,y:", x_peak, y_peak)

    # imfit is 1-indexed
    print("Suggested imfit X0,Y0:", x_peak + 1, y_peak + 1)