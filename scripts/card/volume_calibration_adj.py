#!/usr/bin/env python3
"""
volume_calibration_adj.py -- READ-ONLY. The MARKET-ADJUSTED variant of volume_calibration.py. Writes nothing.
THE FLAW IT TESTS. The volume ratio compares each stock with its OWN trailing history, not with other stocks that day. Quarterly options expiry, index reconstitution, half-days and crash days lift volume for
nearly every stock without any stock-specific news, so those spikes are not information about the stock. That raises the spike rate on CALM and MID days (f) and on every other group, and blurs the calibration.
THE VARIANT. Each stock's volume ratio on a day is divided by the MEDIAN volume ratio across all stocks that day (a day needs at least 100 volume ratios; other days drop out of every population). Everything else
is volume_calibration.py unchanged, including its pre-set rule (degeneracy check, then consistency check across thresholds) and its bootstrap, because it is that very script run with the adjusted ratio.
The raw run on the real data (results/2026-10-19/volume_calibration.out, committed) read: spike rate at 2.0x: CALM 2.6%, MID 7.7%, BIG 53.0%, known information 86.6%; pi_upper 0.75 / 0.62 / 0.51 at
1.5x / 2.0x / 3.0x (spread 0.24, NOT CONSISTENT); pi_lower at 2.0x 0.31; era pi_upper 0.66 / 0.62 / 0.56.
Usage:   python3 -u scripts/card/volume_calibration_adj.py        Needs: the same as volume_calibration.py.
PREDICTIONS (before the run): the adjustment lowers the 2.0x spike rate on CALM days to 2.0% or less and on MID days to 6.5% or less; it lowers s (std) by 2 points or more; pi_upper at 2.0x stays within 0.05 of
the raw 0.62; the consistency spread stays above 0.10 (probability 70%: the drift across thresholds comes from information having graded volume, which a market adjustment does not change); and the fall in
pi_upper across eras (0.66 to 0.56) persists.
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import unrecorded_candidates as uc
import volume_calibration as vc

MIN_STOCKS_PER_DAY = 100
_raw_vol_ratio = uc.vol_ratio


def adjusted_vol_ratio(VOL):
    VR = _raw_vol_ratio(VOL)
    fin = np.isfinite(VR)
    day_med = np.nanmedian(np.where(fin, VR, np.nan), axis=0)
    good = (fin.sum(axis=0) >= MIN_STOCKS_PER_DAY) & (day_med > 0)
    print("market adjustment: days with at least %d volume ratios: %d of %d; median of the daily cross-sectional medians %.3f (1.0 = a typical day); 95th percentile %.3f; maximum %.3f" % (
        MIN_STOCKS_PER_DAY, int(good.sum()), VR.shape[1], float(np.nanmedian(day_med[good])), float(np.nanpercentile(day_med[good], 95)), float(np.nanmax(day_med[good]))), flush=True)
    return VR / np.where(good, day_med, np.nan)[None, :]


if __name__ == "__main__":
    uc.vol_ratio = adjusted_vol_ratio
    vc.main()
