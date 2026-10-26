"""Export the 2D Lya maps from extract_lya_maps.py (iter2 products) as FITS with WCS.

Run from /home/alberto/cosmos/LRD/MUSE. Reads only; writes to OUT_DIR.
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS

MUSE = Path('/home/alberto/cosmos/LRD/MUSE')
sys.path.insert(0, str(MUSE))
import extract_lya_maps as E  # noqa: E402
from make_lya_three_panel_figures import NARROWBAND_SB_MAP_TARGETS  # noqa: E402

OUT_DIR = Path(sys.argv[1])
OUT_DIR.mkdir(parents=True, exist_ok=False)
(OUT_DIR / 'png').mkdir()

for cube_path in E.list_trimmed_cubes(MUSE / 'trimmed_cubes'):
    target = cube_path.name.split('__')[0]
    z = E.redshift_dict[target]
    stem = E.sanitize_stem(cube_path.name.replace('.fits', ''))
    npz = np.load(MUSE / 'Lya_maps/iterative_refined' / f'{stem}__iter2_spectral_products.npz')

    with fits.open(cube_path, memmap=True) as hdul:
        _, cube, hdr = E.find_cube_hdu(hdul)
        cube = np.asarray(cube, dtype=np.float64)
        stat = np.asarray(hdul['STAT'].data, dtype=np.float64) if 'STAT' in hdul else None
        wave = E.wavelength_axis_angstrom(hdr, cube.shape[0])
        pix = E.spatial_pixel_scale_arcsec(hdr)
        cx, cy = E.center_position(cube[0])
        mask, *_ = E.build_whitelight_contaminant_mask(
            cube_data=cube, center=(float(cx), float(cy)),
            central_radius_pix=(E.APERTURE_DIAMETER_ARCSEC / 2.0) / pix)

    # Observed SB scale (no (1+z)^4 dimming correction): counts*dlambda per arcsec^2 -> cgs
    sb = E.lya_surface_brightness_scale_cgs(hdr, wave, pix)
    fc = float(npz['fitted_center_iter'])
    win = np.abs(wave - fc) <= E.WINDOW_WIDTH_ANGSTROM / 2.0
    cm = cube.copy()
    cm[:, mask] = np.nan
    nb = np.nansum(cm[win], axis=0)
    # Sanity: reproduce the stored 20 A map
    assert np.allclose(nb, npz['flux_map_iter'], rtol=1e-4, atol=1e-3 * np.nanstd(nb)), target
    wmap = np.asarray(npz['weighted_map_iter'], dtype=np.float64)

    def masked(a):
        a = np.array(a, dtype=np.float32)
        a[mask] = np.nan
        return a

    wcs = WCS(hdr).celestial
    base = wcs.to_header()
    for k in ('BUNIT',):
        base.pop(k, None)

    ph = fits.PrimaryHDU()
    ph.header['OBJECT'] = target
    ph.header['Z_CAT'] = (z, 'catalog redshift')
    ph.header['LYA_CEN'] = (fc, '[A] fitted Lya centre (iter2, obs., air)')
    ph.header['Z_LYA'] = (fc / E.LYA_REST_ANGSTROM - 1.0, 'redshift of fitted Lya peak')
    ph.header['PIXSCALE'] = (pix, '[arcsec/pix]')
    ph.header['DIMFAC'] = (E.sb_redshift_scale(z), '((1+z)/4)^4, NOT applied')
    ph.header['MU'] = (E.magnification_dict.get(target, 1.0), 'lensing magnification (SB unchanged)')
    ph.header['SRCCUBE'] = cube_path.name
    ph.header['XCEN'] = (float(cx) + 1, 'aperture centre x (FITS 1-based)')
    ph.header['YCEN'] = (float(cy) + 1, 'aperture centre y (FITS 1-based)')
    hdus = [ph]

    h = base.copy()
    h['EXTNAME'] = 'LYA_NB20'
    h['BUNIT'] = 'erg s-1 cm-2 arcsec-2'
    h['COMMENT'] = f'Lya SB: sum over {fc - 10:.2f}-{fc + 10:.2f} A (20 A centred on fitted Lya).'
    h['COMMENT'] = 'Observed SB, no continuum subtraction, no (1+z)^4 correction.'
    h['COMMENT'] = 'NaN = white-light contaminant mask.'
    hdus.append(fits.ImageHDU(masked(nb * sb), header=h))

    if stat is not None:
        s = stat.copy()
        s[:, mask] = np.nan
        h = base.copy()
        h['EXTNAME'] = 'LYA_NB20_ERR'
        h['BUNIT'] = 'erg s-1 cm-2 arcsec-2'
        h['COMMENT'] = '1 sigma from the cube STAT variance (no covariance correction).'
        hdus.append(fits.ImageHDU(masked(np.sqrt(np.nansum(s[win], axis=0)) * sb), header=h))

    h = base.copy()
    h['EXTNAME'] = 'LYA_WEIGHTED'
    h['BUNIT'] = 'erg s-1 cm-2 arcsec-2'
    h['COMMENT'] = 'Lya-profile-weighted map (spectral weights = fitted line model, sum to 1),'
    h['COMMENT'] = 'times one spectral pixel; as in the LyaMap_weighted_iter2 PNG. A S/N-optimized'
    h['COMMENT'] = 'image, NOT total line SB: use LYA_NB20 for fluxes.'
    hdus.append(fits.ImageHDU(masked(wmap * sb), header=h))

    if target in NARROWBAND_SB_MAP_TARGETS:
        dv = NARROWBAND_SB_MAP_TARGETS[target]
        lam = E.LYA_REST_ANGSTROM * (1 + z)
        half = lam * dv / E.C_KMS
        nbw = (wave >= lam - half) & (wave <= lam + half)
        h = base.copy()
        h['EXTNAME'] = 'LYA_NB_EXPECTED'
        h['BUNIT'] = 'erg s-1 cm-2 arcsec-2'
        h['COMMENT'] = f'Faint target: sum over +/-{dv:.0f} km/s about the catalog-z Lya ({lam:.2f} A),'
        h['COMMENT'] = 'the map used in the three-panel figure for this target.'
        hdus.append(fits.ImageHDU(masked(np.nansum(cm[nbw], axis=0) * sb), header=h))

    fits.HDUList(hdus).writeto(OUT_DIR / f'{target}_Lya_maps.fits')
    shutil.copy2(MUSE / 'Lya_maps/iterative_refined' / f'{stem}__LyaMap_weighted_iter2.png',
                 OUT_DIR / 'png' / f'{target}_LyaMap_weighted.png')
    print(target, [x.name for x in hdus[1:]], f'NB peak {np.nanmax(nb * sb):.2e}')
