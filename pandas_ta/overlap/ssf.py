# -*- coding: utf-8 -*-
from numpy import cos as npCos
from numpy import exp as npExp
from numpy import pi as npPi
from numpy import sqrt as npSqrt
from pandas import Series
from pandas_ta.utils import get_offset, verify_series


def ssf(close, length=None, poles=None, offset=None, **kwargs):
    """Indicator: Ehler's Super Smoother Filter (SSF)"""
    # Validate Arguments
    close = verify_series(close)
    length = int(length) if length and length > 0 else 10
    poles = int(poles) if poles in [2, 3] else 2
    offset = get_offset(offset)

    # Calculate Result
    m = close.size
    ssf = close.copy()
    ssf[poles:] = 0

    if poles == 3:
        x = npPi / length # x = PI / n
        a0 = npExp(-x) # e^(-x)
        b0 = 2 * a0 * npCos(npSqrt(3) * x) # 2e^(-x)*cos(3^(.5) * x)
        c0 = a0 * a0 # e^(-2x)
        
        c4 = c0 * c0 # e^(-4x)
        c3 = -c0 * (1 + b0) # -e^(-2x) * (1 + 2e^(-x)*cos(3^(.5) * x))
        c2 = c0 + b0 # e^(-2x) + 2e^(-x)*cos(3^(.5) * x)
        c1 = 1 - c2 - c3 - c4

        for i in range(0, m):
            ssf.iloc[i] = c1 * close.iloc[i] + c2 * ssf.iloc[i - 1] + c3 * ssf.iloc[i - 2] + c4 * ssf.iloc[i - 3]

    else: # poles == 2
        x = npPi * npSqrt(2) / length # x = PI * 2^(.5) / n
        a0 = npExp(-x) # e^(-x)
        a1 = -a0 * a0 # -e^(-2x)
        b1 = 2 * a0 * npCos(x) # 2e^(-x)*cos(x)
        c1 = 1 - a1 - b1 # e^(-2x) - 2e^(-x)*cos(x) + 1

        for i in range(0, m):
            ssf.iloc[i] = c1 * close.iloc[i] + b1 * ssf.iloc[i - 1] + a1 * ssf.iloc[i - 2]

    # Offset
    if offset != 0:
        ssf = ssf.shift(offset)

    # Name & Category
    ssf.name = f"SSF_{length}_{poles}"
    ssf.category = "overlap"

    return ssf


ssf.__doc__ = \
"""Ehler's Super Smoother Filter (SSF)

Ehler's solution to reduce lag and remove aliasing noise with his research in
aerospace analog filter design. © 2013 John F. Ehlers

Sources:
    http://www.stockspotter.com/files/PredictiveIndicators.pdf
    https://www.tradingview.com/script/VdJy0yBJ-Ehlers-Super-Smoother-Filter/
    https://www.mql5.com/en/code/588
    https://www.mql5.com/en/code/589

Calculation:
    Default Inputs:
        length=10, poles=[2, 3]

Args:
    close (pd.Series): Series of 'close's
    length (int): It's period. Default: 10
    poles (int): The number of poles to use, either 2 or 3. Default: 2
    offset (int): How many periods to offset the result. Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""
