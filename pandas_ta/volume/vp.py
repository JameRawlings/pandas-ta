# -*- coding: utf-8 -*-
from numpy import array_split
from numpy import mean
from pandas import cut, concat, DataFrame
from pandas_ta.utils import signed_series, verify_series


def vp(close, volume, width=None, **kwargs):
    """Indicator: Volume Profile (VP)"""
    # Validate arguments
    width = int(width) if width and width > 0 else 10
    close = verify_series(close, width)
    volume = verify_series(volume, width)
    sort_close = kwargs.pop("sort_close", False)

    if close is None or volume is None: return

    # Setup
    signed_price = signed_series(close, initial=1)
    pos_volume = signed_price[signed_price > 0] * volume
    neg_volume = signed_price[signed_price < 0] * -volume
    vp = concat([close, pos_volume, neg_volume], axis=1)

    close_col = 'close'
    high_price_col = 'high_close'
    low_price_col = 'low_close'
    mean_price_col = 'mean_close'
    pos_volume_col = 'pos_volume'
    neg_volume_col = 'neg_volume'
    total_volume_col = 'total_volume'

    vp.columns = [close_col, pos_volume_col, neg_volume_col]

    # sort_close: Sort by close before splitting into ranges. Default: False
    # If False, it sorts by date index or chronological versus by price

    if sort_close:
        vp[mean_price_col] = vp[close_col]
        vpdf = vp.groupby(cut(vp[close_col], width, include_lowest=True, precision=2)).agg({
            mean_price_col: mean,
            pos_volume_col: sum,
            neg_volume_col: sum,
        })
        vpdf[low_price_col] = [x.left for x in vpdf.index]
        vpdf[high_price_col] = [x.right for x in vpdf.index]
        vpdf = vpdf.reset_index(drop=True)
        vpdf = vpdf[[low_price_col, mean_price_col, high_price_col, pos_volume_col, neg_volume_col]]
    else:
        vp_ranges = array_split(vp, width)
        result = ({
            low_price_col: r[close_col].min(),
            mean_price_col: r[close_col].mean(),
            high_price_col: r[close_col].max(),
            pos_volume_col: r[pos_volume_col].sum(),
            neg_volume_col: r[neg_volume_col].sum(),
        } for r in vp_ranges)
        vpdf = DataFrame(result)
    vpdf[total_volume_col] = vpdf[pos_volume_col] + vpdf[neg_volume_col]

    # Handle fills
    if "fillna" in kwargs:
        vpdf.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        vpdf.fillna(method=kwargs["fill_method"], inplace=True)

    # Name and Categorize it
    vpdf.name = f"VP_{width}"
    vpdf.category = "volume"

    return vpdf


vp.__doc__ = \
"""Volume Profile (VP)

Calculates the Volume Profile by slicing price into ranges.
Note: Value Area is not calculated.

Sources:
    https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:volume_by_price
    https://www.tradingview.com/wiki/Volume_Profile
    http://www.ranchodinero.com/volume-tpo-essentials/
    https://www.tradingtechnologies.com/blog/2013/05/15/volume-at-price/

Calculation:
    Default Inputs:
        width=10

    vp = pd.concat([close, pos_volume, neg_volume], axis=1)
    vp_ranges = np.array_split(vp, width)
    result = ({high_close, low_close, mean_close, neg_volume, pos_volume} foreach range in vp_ranges)
    vpdf = pd.DataFrame(result)
    vpdf['total_volume'] = vpdf['pos_volume'] + vpdf['neg_volume']

Args:
    close (pd.Series): Series of 'close's
    volume (pd.Series): Series of 'volume's
    width (int): How many ranges to distrubute price into. Default: 10

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method
    sort_close (value, optional): Whether to sort by close before splitting
        into ranges. Default: False

Returns:
    pd.DataFrame: New feature generated.
"""
