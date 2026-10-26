import matplotlib.pyplot as plt
import numpy as np

from astropy.io import fits
from astropy.visualization import ImageNormalize, AsinhStretch
from matplotlib.colors import SymLogNorm, AsinhNorm

def plot_model_residual(
    data, model, residual,
    data_title="Data", model_title="Model", residual_title="Residual",
    cmap="RdBu_r", xlim=None, ylim=None
):
    # Shared symmetric limits using all three images
    values = np.concatenate([
        np.asarray(img).ravel() for img in (data, model, residual)
    ])
    values = values[np.isfinite(values)]

    vmax = max(np.percentile(np.abs(values), 99.95), np.finfo(float).eps)

    # Linear near zero, logarithmic at larger positive/negative values
    norm = AsinhNorm(
    linear_width=0.2 * vmax,
    vmin=-vmax,
    vmax=vmax
    )

    fig, ax = plt.subplots(
        1, 3, figsize=(12, 4), constrained_layout=True
    )

    for a, img, title in zip(
        ax,
        (data, model, residual),
        (data_title, model_title, residual_title)
    ):
        im = a.imshow(img, origin="lower", cmap=cmap, norm=norm)
        a.set_title(title)
        a.set_xlabel("x [pixels]")

        if xlim is not None:
            a.set_xlim(xlim)
        if ylim is not None:
            a.set_ylim(ylim)

    ax[0].set_ylabel("y [pixels]")

    # One colorbar for all three panels
    cbar = fig.colorbar(
    im, ax=ax, shrink=0.85, pad=0.02,
    extend="both",
    ticks=vmax * np.array([-1, -0.3, 0, 0.3, 1])
    )
    cbar.set_label("Intensity")
    cbar.ax.minorticks_off()
    cbar.ax.set_yticklabels(
        [f"{v:.2g}" for v in cbar.get_ticks()]
    )

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