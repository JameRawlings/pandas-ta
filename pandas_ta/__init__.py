name = "pandas_ta"
"""
.. moduleauthor:: Kevin Johnson
"""
from pkg_resources import get_distribution, DistributionNotFound
import os.path

try:
    _dist = get_distribution('pandas_ta')
    # Normalize case for Windows systems
    dist_loc = os.path.normcase(_dist.location)
    here = os.path.normcase(__file__)
    if not here.startswith(os.path.join(dist_loc, 'pandas_ta')):
        # not installed, but there is another version that *is*
        raise DistributionNotFound
except DistributionNotFound:
    __version__ = 'Please install this project with setup.py'
else:
    __version__ = _dist.version

# Performance
from .performance.log_return import log_return
from .performance.percent_return import percent_return
from .performance.trend_return import trend_return

# Statistics
from .statistics.kurtosis import kurtosis
from .statistics.mad import mad
from .statistics.median import median
from .statistics.quantile import quantile
from .statistics.skew import skew
from .statistics.stdev import stdev
from .statistics.variance import variance
from .statistics.zscore import zscore

# Trend
from .trend.adx import adx
from .trend.amat import amat
from .trend.aroon import aroon
from .trend.decreasing import decreasing
from .trend.dpo import dpo
from .trend.increasing import increasing
from .trend.long_run import long_run
from .trend.qstick import qstick
from .trend.short_run import short_run
from .trend.vortex import vortex

# Volatility
from .volatility.accbands import accbands
from .volatility.atr import atr
from .volatility.bbands import bbands
from .volatility.donchian import donchian
from .volatility.kc import kc
from .volatility.massi import massi
from .volatility.natr import natr
from .volatility.true_range import true_range

# Volume
from .volume.ad import ad
from .volume.adosc import adosc
from .volume.aobv import aobv
from .volume.cmf import cmf
from .volume.efi import efi
from .volume.eom import eom
from .volume.mfi import mfi
from .volume.nvi import nvi
from .volume.obv import obv
from .volume.pvi import pvi
from .volume.pvol import pvol
from .volume.pvt import pvt
from .volume.vp import vp

# DataFrame Extension
from .core import *

