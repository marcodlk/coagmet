from datetime import datetime
from io import StringIO
import requests
# import warnings

import pandas as pd
import numpy as np

from .exceptions import BadRequestError

daily_data_fmt = '''
Datetime (in the format YYYY-MM-DD)
Mean Temperature (Celsius)
Maximum Temperature (Celsius)
Time of Maximum Temperature (HH:MM:SS)
Minimum Temperature (Celsius)
Time of Minimum Temperature (HH:MM:SS)
Vapor Pressure (kPa)
Maximum Relative Humidity (Fraction)
Time of Maximum Relative Humidity (HH:MM:SS)
Minimum Relative Humidity (Fraction)
Time of Minimum Relative Humidity (HH:MM:SS)
Solar Radiation (MJ/m^2)
Wind_Run (km/day)
Precipitation (millimeters)
Maximum Soil Temperature at 5cm (Celsius)
Time of Maximum Soil Temperature at 5cm (HH:MM:SS)
Minimum Soil Temperature at 5cm (Celsius)
Time of Minimum Soil Temperature at 5cm (HH:MM:SS)
Maximum Soil Temperature at 15cm (Celsius)
Time of Maximum Soil Temperature at 15cm (HH:MM:SS)
Minimum Soil Temperature at 15cm (Celsius)
Time of Minimum Soil Temperature at 15cm (HH:MM:SS)
Battery Voltage
Year of data
Maximum daily wind gust (m/s)
Time of maximum daily wind gust (min into day NOT HH:MM as other max/min)
Direction of maximum daily wind gust (deg)
ASCE Reference Evapotranspiration Model (mm)*
Penman-Kimberly Ref. Evapotranspiration Model (mm)*
Summed hourly ASCE Ref. ET (mm)*
'''.strip() 

daily_columns = [
    'datetime',
    'mean_temp',
    'max_temp',
    'max_temp_time',
    'min_temp',
    'min_temp_time',
    'vapor_pressure',
    'max_rel_humidity',
    'max_rel_humidity_time',
    'min_rel_humidity',
    'min_rel_humidity_time',
    'solar_radiation',
    'wind_run',
    'precipitation',
    'max_soil_temp_5cm',
    'max_soil_temp_5cm_time',
    'min_soil_temp_5cm',
    'min_soil_temp_5cm_time',
    'max_soil_temp_15cm',
    'max_soil_temp_15cm_time',
    'min_soil_temp_15cm',
    'min_soil_temp_15cm_time',
    'battery_voltage',
    'year',
    'max_daily_wind_gust',
    'max_daily_wind_gust_time',
    'dir_daily_wind_gust'
]

daily_columns_etr = [
    'asce_etr',
    'pk_etr',
    'sum_hourly_asce_etr'
]

hourly_data_fmt = '''
Datetime (in the format YYYY-MM-DD HH:MM:SS)
Mean Temperature (Celsius)
Relative Humidity (Fraction)
Vapor Pressure (kPa)
Solar Radiation (kJ/m^2 * min)
Mean Wind Speed (m/s)
Vector Average Wind Direction (in Degrees, 0 and 360 being north)
Standard Deviation of Wind Direction (Degrees)
Precipitation (millimeters)
Mean Soil Temp at 5cm (Celsius)
Mean Soil Temp at 15cm (Celsius)
Wind Gust (m/s)
Wind Gust Time (minutes into day)
Wind Gust Direction (Degrees)
ASCE hourly Reference Evapotranspiration Model (mm)*
'''.strip()

hourly_columns = [
    'datetime',
    'mean_temp',
    'rel_humidity',
    'vapor_pressure',
    'solar_radiation',
    'mean_wind_speed',
    'va_wind_dir',
    'std_wind_dir',
    'precipitation',
    'mean_soil_temp_5cm',
    'mean_soil_temp_15cm',
    'wind_gust',
    'wind_gust_time',
    'wind_gust_dir',
]

hourly_columns_etr = [
    'asce_etr_hourly'
]

fivemin_data_fmt = '''
Datetime (in the format YYYY-MM-DD HH:MM:SS)
Battery Voltage
Mean Temperature (Celsius)
Relative Humidity (Fraction)
Vapor Pressure (kPa)
Solar Radiation (kJ/m^2 * min)
Mean Wind Speed (m/s)
Vector Average Wind Direction (in Degrees, 0 and 360 being north)
Standard Deviation of Wind Direction (Degrees)
Precipitation (millimeters)
Mean Soil Temp at 5cm (Celsius)
Mean Soil Temp at 15cm (Celsius)
Wind Gust (m/s)
Wind Gust Time (minutes into day)
Wind Gust Direction (Degrees)
'''.strip()

fivemin_columns = [
    'datetime',
    'battery_voltage',
    'mean_temp',
    'rel_humidity',
    'vapor_pressure',
    'solar_radiation',
    'mean_wind_speed',
    'va_wind_dir',
    'std_wind_dir',
    'precipitation',
    'mean_soil_temp_5cm',
    'mean_soil_temp_15cm',
    'wind_gust',
    'wind_gust_time',
    'wind_gust_dir',
]

fivemin_columns_etr = []

def build_url_raw(station, start_date=None, end_date=None, 
                  daily=True, hourly=False, fivemin=False, 
                  qc=True, etr=True):
    url = 'https://coagmet.colostate.edu/rawdata_results.php?'
    url += 'station=' + station
    if start_date:
        url += '&start_date=' + start_date
    if end_date:
        url += '&end_date=' + end_date
    if daily:
        url += '&daily=1'
    if hourly:
        url += '&hourly=1'
    if fivemin:
        url += '&5min=1'
    if qc:
        url += '&qc=1'
    if etr:
        url += '&etr=1'
    return url

def get_raw(station, start_date=None, end_date=None, 
            freq='daily', qc=True, etr=True):
    
    if freq == 'daily':
        daily, hourly, fivemin = True, False, False
        columns = ['station'] + daily_columns
        if etr:
            columns += daily_columns_etr
    elif freq == 'hourly':
        daily, hourly, fivemin = False, True, False
        columns = ['station'] + hourly_columns
        if etr:
            columns += hourly_columns_etr
    elif freq == '5min':
        daily, hourly, fivemin = False, False, True
        columns = ['station'] + fivemin_columns
        if etr:
            columns += fivemin_columns_etr
    else:
        raise ValueError('freq must be one of: [daily, hourly, 5min]'
                         ' but received: {}'.format(freq))
    url = build_url_raw(station, start_date, end_date,
                        daily, hourly, fivemin,
                        qc, etr)
    csv = requests.get(url).text
        
    df = pd.read_csv(StringIO(csv), header=None, names=columns, index_col='datetime')
    
    if len(df) == 1 and df[df.columns[1:]].isnull().values.all():
        raise BadRequestError(csv)
        
    return df

    
class RawData:
    
    def __init__(self,
                 station,
                 freq='daily', 
                 qc=True, 
                 etr=True,
                 columns=None,
                 ignore=['station', 'year'],
                 ignore_temporal=True):
        self.station = station
        self.freq = freq
        self.qc = qc
        self.etr = etr
        self.columns = columns
        self.ignore = ignore
        self.ignore_temporal = ignore_temporal
        
    def get(self, start_date, end_date=None):
        if end_date is None:
            end_date = start_date
        df = get_raw(self.station, start_date, end_date,
                     self.freq, self.qc, self.etr)
        if self.columns:
            return df[self.columns]
        else:
            drop_columns = []
            if self.ignore:
                for col in self.ignore:
                    if col not in df:
                        # warnings.warn('Ignoring a column that already'
                        #               ' doesn\'t exist: {}'.format(col))
                        pass
                    else:
                        drop_columns.append(col)
            if self.ignore_temporal:
                drop_columns += [col for col in df if 'time' in col]
            df.drop(drop_columns, axis=1, inplace=True)
            return df
        
    def __getitem__(self, key):
        if isinstance(key, str):
            return self.get(key)
        elif isinstance(key, slice):
            df = self.get(key.start, key.stop)
            if key.step is not None:
                df = df[::key.step]
            return df
        else:
            raise ValueError()

__all__ = ['RawData']