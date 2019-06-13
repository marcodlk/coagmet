=====
Usage
=====

--------------
Stations Index
--------------

Initialize :class:`~coagmet.stations.Stations` object::

    >>> import coagmet
    >>> stations = coagmet.Stations()

Get station index table as dataframe::

    >>> stations_df = stations.get()
    >>> stations_df.columns.tolist()
    Index(['Station Name', 'Location', 'Latitude', 'Longitude', 'Elev. (ft)',
           'First Obs.', 'Last Obs.', 'Irrigation Type'],
          dtype='object')

Find nearest station to a location, defined by latitude & longitude::

    >>> station_id = stations.find_nearest_station(38.8, 107.8)
    >>> station_id
    'HOT01'

Find 3 nearest stations to a location::

    >>> station_ids = stations.find_nearest_stations(38.8, 107.8, n=3)
    >>> station_ids
    Index(['HOT01', 'CDG01', 'EKT01'], dtype='object')


--------
Raw Data
--------

Use :class:`~coagmet.raw_data.RawData` object to fetch 5min raw data
for station 'DRG01' from Januray 1, 2019 until January 2, 2019::

    >>> import coagmet
    >>> raw_5min = coagmet.RawData('DRG01', freq='5min)
    >>> df_5min = raw_5min.get('2019-01-01', '2019-01-02')
    >>> df_5min.shape
    (576, 13)


Use :class:`~coagmet.raw_data.RawData` object to fetch hourly raw data 
for station 'DRG01' from January 1, 2019 until January 8, 2019::

    >>> raw_hourly = coagmet.RawData('DRG01', freq='hourly')
    >>> df_hourly = raw_hourly.get('2019-01-01', '2019-01-08')
    >>> df_hourly.shape
    (192, 13)

Use :class:`~coagmet.raw_data.RawData` object to fetch hourly raw data 
for station 'DRG01' from January 1, 2019 until January 31, 2019::

    >>> raw_daily = coagmet.RawData('DRG01', freq='daily')
    >>> df_daily = raw_daily.get('2019-01-01', '2019-01-31')
    >>> df_daily.shape
    (31, 19)
