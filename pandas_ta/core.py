# -*- coding: utf-8 -*-
import time
import pandas as pd
from pandas.core.base import PandasObject

from .overlap import *
from .performance import *
from .statistics import *
from .utils import *


class BasePandasObject(PandasObject):
    """Simple PandasObject Extension

    Ensures the DataFrame is not empty and has columns.

    Args:
        df (pd.DataFrame): Extends Pandas DataFrame
    """
    def __init__(self, df, **kwargs):
        if df.empty: return

        if len(df.columns) > 0:
            self._df = df
        else:
            raise AttributeError(f"[X] No columns!")

    def __call__(self, kind, *args, **kwargs):
        raise NotImplementedError()


@pd.api.extensions.register_dataframe_accessor('ta')
class AnalysisIndicators(BasePandasObject):
    """AnalysisIndicators is class that extends the Pandas DataFrame via
    Pandas @pd.api.extensions.register_dataframe_accessor('name') decorator.

    This Pandas Extension is named 'ta' for Technical Analysis that allows us
    to apply technical indicators with an one extension.  Even though 'ta' is
    now a Pandas DataFrame Extension, you can still call the Indicators
    individually. However many of the Indicators have been updated and new ones
    added, so make sure to check help.
    
    By default the 'ta' extensions uses lower case column names: open, high,
    low, close, and volume.  You can override the defaults but providing the
    it's replacement name when calling the indicator.  For example, to call the
    indicator hl2().  

    With 'default' columns: open, high, low, close, and volume.
    >>> df.ta.hl2()
    >>> df.ta(kind='hl2')

    With DataFrame columns: Open, High, Low, Close, and Volume.
    >>> df.ta.hl2(high='High', low='Low')
    >>> df.ta(kind='hl2', high='High', low='Low')

    Args:
        kind (str, optional): Default: None.  Name of the indicator.  Converts
            kind to lowercase before calling.
        timed (bool, optional): Default: False.  Curious about the execution
            speed?  Well it's not ground breaking, but you can enable with True.
        kwargs: Extension specific modifiers.
            append (bool, optional):  Default: False.  When True, it appends to
            result column(s) of the indicator onto the DataFrame.

    Returns:
        Most Indicators will return a Pandas Series.  Others like MACD, BBANDS,
        KC, et al will return a Pandas DataFrame.  Ichimoku on the other hand
        will return two DataFrames, the Ichimoku DataFrame for the known period
        and a Span DataFrame for the future of the Span values.

    Let's get started!

    1. Loading the 'ta' module:
    >>> import pandas as pd
    >>> import ta as ta

    2. Load some data:
    >>> df = pd.read_csv('AAPL.csv', index_col='date', parse_dates=True)
    
    3. Help!
    3a. General Help:
    >>> help(df.ta)
    >>> df.ta()
    3a. Indicator Help:
    >>> help(ta.apo)
    3b. Indicator Extension Help:
    >>> help(df.ta.apo)

    4. Ways of calling an indicator.
    4a. Calling just the MACD indicator without 'ta' DataFrame extension.
    >>> ta.apo(df['close'])
    4b. Calling just the MACD indicator with 'ta' DataFrame extension.
    >>> df.ta.apo()
    4c. Calling using kind.
    >>> df.ta(kind='apo')

    5. Working with kwargs
    5a. Append the result to the working df.
    >>> df.ta.apo(append=True)
    5b. Timing an indicator.
    >>> apo = df.ta(kind='apo', timed=True)
    >>> print(apo.timed)
    """
    def __call__(self, kind=None, alias=None, timed=False, **kwargs):
        try:
            if isinstance(kind, str):
                kind = kind.lower() 
                fn = getattr(self, kind)

                if timed:
                    stime = time.time()

                # Run the indicator
                indicator = fn(**kwargs)

                if timed:
                    time_diff = time.time() - stime
                    ms = time_diff * 1000
                    indicator.timed = f"{ms:2.3f} ms ({time_diff:2.3f} s)"
                    # print(f"execution time: {indicator.timed}")

                # Add an alias if passed
                if alias:
                    indicator.alias = f"{alias}"
                
                return indicator
            else:
                self.help()

        except:
            self.help()


    def _append(self, result=None, **kwargs):
        """Appends a Pandas Series or DataFrame columns to self._df."""
        if 'append' in kwargs and kwargs['append']:
            df = self._df
            if df is None or result is None: return
            else:                
                if isinstance(result, pd.DataFrame):
                    for i, column in enumerate(result.columns):
                        df[column] = result.iloc[:,i]
                else:
                    df[result.name] = result


    def _get_column(self, series, default):
        """Attempts to get the correct series or 'column' and return it."""
        df = self._df
        if df is None: return

        # Explicit passing a pd.Series to override default.
        if isinstance(series, pd.Series):
            return series
        # Apply default if no series nor a default.
        elif series is None or default is None:
            return df[default]
        # Ok.  So it's a str.
        elif isinstance(series, str):
            # Return the df column since it's in there.
            if series in df.columns:
                return df[series]
            else:
                # Attempt to match the 'series' because it was likely misspelled.
                matches = df.columns.str.match(series, case=False)
                match = [i for i, x in enumerate(matches) if x]
                # If found, awesome.  Return it or return the 'series'.
                NOT_FOUND = f"[X] Ooops!!!: It's {series not in df.columns}, the series '{series}' not in {', '.join(list(df.columns))}"
                return df.iloc[:,match[0]] if len(match) else print(NOT_FOUND)


    def constants(self, apply, lower_bound=-100, upper_bound=100, every=1):
        """Constants

        Useful for indicator levels or if you need some constant value.

        Add constant '1' to the DataFrame
        >>> df.ta.constants(True, 1, 1, 1)
        Remove constant '1' to the DataFrame
        >>> df.ta.constants(False, 1, 1, 1)

        Adding constants that range of constants from -4 to 4 inclusive
        >>> df.ta.constants(True, -4, 4, 1)
        Removing constants that range of constants from -4 to 4 inclusive
        >>> df.ta.constants(False, -4, 4, 1)

        Args:
            apply (bool): Default: None.  If True, appends the range of constants to the
                working DataFrame.  If False, it removes the constant range from the working
                DataFrame.
            lower_bound (int): Default: -100.  Lowest integer for the constant range.
            upper_bound (int): Default: 100.  Largest integer for the constant range.
            every (int): Default: 10.  How often to include a new constant.
        
        Returns:
            Returns nothing to the user.  Either adds or removes constant ranges from the
            working DataFrame.
        """
        levels = [x for x in range(lower_bound, upper_bound + 1) if x % every == 0]
        if apply:
            for x in levels:
                self._df[f'{x}'] = x
        else:
            for x in levels:
                del self._df[f'{x}']


    def indicators(self, **kwargs):
        """Indicator list"""
        header = f"pandas.ta - Technical Analysis Indicators"
        helper_methods = ['indicators', 'constants'] # Public non-indicator methods
        exclude_methods = kwargs.pop('exclude', None)
        as_list = kwargs.pop('as_list', False)
        ta_indicators = list((x for x in dir(pd.DataFrame().ta) if not x.startswith('_') and not x.endswith('_')))

        for x in helper_methods:
            ta_indicators.remove(x)

        if isinstance(exclude_methods, list) and exclude_methods in ta_indicators and len(exclude_methods) > 0:
            for x in exclude_methods:
                ta_indicators.remove(x)

        if as_list:
            return ta_indicators

        total_indicators = len(ta_indicators)
        s = f"{header}\nTotal Indicators: {total_indicators}\n"
        if total_indicators > 0:            
            abbr_list = ', '.join(ta_indicators)
            # print(f"{s}Abbreviations:\n    {abbr_list}")
            print(f"{s}Abbreviations:\n    {abbr_list}")
        else:
            print(s)



    # Overlap Indicators
    def dema(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = dema(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def ema(self, close=None, length=None, offset=None, adjust=None, **kwargs):
        close = self._get_column(close, 'close')
        result = ema(close=close, length=length, offset=offset, adjust=adjust, **kwargs)
        self._append(result, **kwargs)
        return result


    def fwma(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = fwma(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def hl2(self, high=None, low=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        result = hl2(high=high, low=low, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def hlc3(self, high=None, low=None, close=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        result = hlc3(high=high, low=low, close=close, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def hma(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = hma(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def ichimoku(self, high=None, low=None, close=None, tenkan=None, kijun=None, senkou=None, offset=None, **kwargs):        
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        # result, span = ichimoku(high=high, low=low, close=close, tenkan=tenkan, kijun=kijun, senkou=senkou, offset=offset, **kwargs)
        result = ichimoku(high=high, low=low, close=close, tenkan=tenkan, kijun=kijun, senkou=senkou, offset=offset, **kwargs)
        self._append(result, **kwargs)
        # return result, span
        return result


    def midpoint(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = midpoint(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def midprice(self, high=None, low=None, length=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        result = midprice(high=high, low=low, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def ohlc4(self, open_=None, high=None, low=None, close=None, offset=None, **kwargs):
        open_ = self._get_column(open_, 'open')
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        result = ohlc4(open_=open_, high=high, low=low, close=close, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def pwma(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = pwma(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def rma(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = rma(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def sma(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = sma(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def t3(self, close=None, length=None, a=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = t3(close=close, length=length, a=a, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def tema(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = tema(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def trima(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = trima(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def vwap(self, high=None, low=None, close=None, volume=None, offset=None, **kwargs):
        high = self._get_column(high, 'high')
        low = self._get_column(low, 'low')
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        result = vwap(high=high, low=low, close=close, volume=volume, offset=offset, **kwargs)
        self._append(result, **kwargs)        
        return result


    def vwma(self, close=None, volume=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        volume = self._get_column(volume, 'volume')
        result = vwma(close=close, volume=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def wma(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = wma(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result



    # Performance Indicators
    def log_return(self, close=None, length=None, cumulative=False, percent=False, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = log_return(close=close, length=length, cumulative=cumulative, percent=percent, offset=offset, **kwargs)
        self._append(result, **kwargs)
        # print(f"result:\n{result}")
        return result


    def percent_return(self, close=None, length=None, cumulative=False, percent=False, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = percent_return(close=close, length=length, cumulative=cumulative, percent=percent, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result



    # Statistics Indicators
    def kurtosis(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = kurtosis(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def mad(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = mad(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def median(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = median(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def quantile(self, close=None, length=None, q=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = quantile(close=close, length=length, q=q, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def skew(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = skew(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def stdev(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = stdev(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def variance(self, close=None, length=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = variance(close=close, length=length, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result


    def zscore(self, close=None, length=None, std=None, offset=None, **kwargs):
        close = self._get_column(close, 'close')
        result = zscore(close=close, length=length, std=std, offset=offset, **kwargs)
        self._append(result, **kwargs)
        return result