from datetime import datetime
from io import StringIO
import requests

import pandas as pd
import numpy as np

from .base import CoagmetData
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

min5_data_fmt = '''
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

min5_columns = [
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

min5_columns_etr = []

def build_url_raw(station, start_date=None, end_date=None, 
                  daily=True, hourly=False, min5=False, 
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
    if min5:
        url += '&5min=1'
    if qc:
        url += '&qc=1'
    if etr:
        url += '&etr=1'
    return url

def get_raw(station, start_date=None, end_date=None, 
            freq='daily', qc=True, etr=True):
    
    if freq == 'daily':
        daily, hourly, min5 = True, False, False
        columns = ['station'] + daily_columns
        if etr:
            columns += daily_columns_etr
    elif freq == 'hourly':
        daily, hourly, min5 = False, True, False
        columns = ['station'] + hourly_columns
        if etr:
            columns += hourly_columns_etr
    elif freq == '5min':
        daily, hourly, min5 = False, False, True
        columns = ['station'] + min5_columns
        if etr:
            columns += min5_columns_etr
    else:
        raise ValueError('freq must be one of: [daily, hourly, 5min]'
                         ' but received: {}'.format(freq))
    url = build_url_raw(station, start_date, end_date,
                        daily, hourly, min5,
                        qc, etr)
    csv = requests.get(url).text
        
    df = pd.read_csv(StringIO(csv), header=None, names=columns, index_col='datetime')
    
    if len(df) == 1 and df[df.columns[1:]].isnull().values.all():
        raise BadRequestError(csv)
        
    return df

    
class RawData(CoagmetData):
        
    def request(self, station, start_date=None, end_date=None, 
                freq='daily', qc=True, etr=True):
        self.df = get_raw(station, start_date, end_date,
                          freq, qc, etr)
        if 'year' in self.df:
            self.df.drop(['year'], axis=1, inplace=True)
        return self
        
    def get_numerical(self):
        drop_columns = ['station'] + [col for col in self.df if 'time' in col]
        return self.df.drop(drop_columns, axis=1)
    
    def get_temporal(self):
        time_columns = [col for col in self.df if 'time' in col]
        return self.df[time_columns]