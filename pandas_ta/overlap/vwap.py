# -*- coding: utf-8 -*-
from .hlc3 import hlc3
from pandas_ta.utils import get_offset, is_datetime_ordered, verify_series

def vwap(high, low, close, volume, offset=None, **kwargs):
    """Indicator: Volume Weighted Average Price (VWAP)"""
    # Validate Arguments
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    volume = verify_series(volume)
    offset = get_offset(offset)

    typical_price = hlc3(high=high, low=low, close=close)

    if not is_datetime_ordered(volume):
        print(f"[!] VWAP volume series is not datetime ordered. Results may not be as expected.")
    if not is_datetime_ordered(typical_price):
        print(f"[!] VWAP price series is not datetime ordered. Results may not be as expected.")

    # Calculate Result
    weighted_price = typical_price * volume
    vwap = weighted_price.groupby(weighted_price.index.to_period('d')).cumsum() / \
           volume.groupby(volume.index.to_period('d')).cumsum()

    # Offset
    if offset != 0:
        vwap = vwap.shift(offset)

    # Name & Category
    vwap.name = "VWAP"
    vwap.category = 'overlap'

    return vwap


vwap.__doc__ = \
"""Volume Weighted Average Price (VWAP)

The Volume Weighted Average Price that measures the average typical price
by volume.  It is typically used with intraday charts to identify general
direction.

Sources:
    https://www.tradingview.com/wiki/Volume_Weighted_Average_Price_(VWAP)
    https://www.tradingtechnologies.com/help/x-study/technical-indicator-definitions/volume-weighted-average-price-vwap/
    https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:vwap_intraday

Calculation:
    tp = typical_price = hlc3(high, low, close)
    tpv = tp * volume
    VWAP = tpv.cumsum() / volume.cumsum()

Args:
    high (pd.Series): Series of 'high's
    low (pd.Series): Series of 'low's
    close (pd.Series): Series of 'close's
    volume (pd.Series): Series of 'volume's
    offset (int): How many periods to offset the result.  Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""
