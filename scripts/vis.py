import matplotlib.pyplot as plt
import numpy as np

from astropy.io import fits
from astropy.visualization import ImageNormalize, AsinhStretch
from matplotlib.colors import SymLogNorm

def plot_model_residual(data, model, residual, data_title="Data", model_title="Model", residual_title="Residual", cmap="RdBu_r", xlim=None, ylim=None):
    vmin = np.percentile(data, 1)
    vmax = np.percentile(data, 99.95)
    norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=AsinhStretch())

    # Symmetric normalization for residual
    rmax = np.nanpercentile(np.abs(residual), 99.5)
    rmax = max(rmax, np.finfo(float).eps)

    norm_res = SymLogNorm(linthresh=0.01*rmax, vmin=-rmax, vmax=rmax, base=10) ##base for hte log effect

    fig, ax = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)

    im0 = ax[0].imshow(data, origin="lower", cmap=cmap, norm=norm)
    ax[0].set_title(data_title)

    ax[1].imshow(model, origin="lower", cmap=cmap, norm=norm)
    ax[1].set_title(model_title)

    im2 = ax[2].imshow(residual, origin="lower", cmap=cmap, norm=norm_res)
    ax[2].set_title(residual_title)

    for a in ax:
        a.set_xlabel("x [pixels]")
        if xlim is not None: a.set_xlim(xlim)
        if ylim is not None: a.set_ylim(ylim)

    ax[0].set_ylabel("y [pixels]")

    cbar1 = fig.colorbar(im0, ax=ax[:2], shrink=0.85, pad=0.02)
    cbar1.set_label("Intensity")

    # Separate colorbar for residual
    cbar2 = fig.colorbar(im2, ax=ax[2], shrink=0.85, pad=0.02)
    cbar2.set_label("Residual intensity")

    plt.show()

def plot_data_psf(data, psf, data_title="Data", psf_title="PSF", cmap="RdBu_r", xlim=None, ylim=None):
    vmin = np.percentile(data, 1)
    vmax = np.percentile(data, 99.95)
    norm = ImageNormalize(vmin=vmin, vmax=vmax, stretch=AsinhStretch())

    fig, ax = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)

    im0 = ax[0].imshow(data, origin="lower", cmap=cmap, norm=norm)
    ax[0].set_title(data_title)

    ax[1].imshow(psf, origin="lower", cmap=cmap, norm = norm)
    ax[1].set_title(psf_title)

    for a in ax:
        a.set_xlabel("x [pixels]")
        if xlim is not None: a.set_xlim(xlim)
        if ylim is not None: a.set_ylim(ylim)

    ax[0].set_ylabel("y [pixels]")

    cbar = fig.colorbar(im0, ax=ax, shrink=0.85, pad=0.02)
    cbar.set_label("Intensity")

    plt.show()