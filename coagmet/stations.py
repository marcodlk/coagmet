import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup

from .exceptions import BadRequestError


def get_stations():

    url = 'https://coagmet.colostate.edu/station_index.php'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features='lxml')
    table = soup.find('table', attrs={'class': 'station-index'})

    output_rows = []
    for table_row in table.findAll('tr'):
        columns = table_row.findAll('td')
        output_row = []
        for column in columns:
            output_row.append(column.text)
        output_rows.append(output_row)

    output_rows[:10]

    values = []
    station_ids = []
    for i, row in enumerate(output_rows):
        if len(row) > 0:
            station_ids.append(row[0])
            row_vals = []
            for val in row[1:]:
                try:
                    val = float(val)
                except ValueError:
                    pass
                row_vals.append(val)
            values.append(row_vals)

    values = np.array(values)

    headers = [header.text for header in table.findAll('th')]
    headers = headers[:len(headers)]
    headers.remove('ID')

    dict_ = {headers[i]: values[:, i] for i in range(values.shape[1])}

    df = pd.DataFrame(dict_, index=station_ids)
    
    if len(df) == 1 and df[df.columns[1:]].isnull().values.all():
        raise BadRequestError(response.text)
        
    df['Latitude'] = df['Latitude'].astype(float)
    df['Longitude'] = df['Longitude'].astype(float)
    df['Elev. (ft)'] = df['Elev. (ft)'].astype(float)

    for i, row in df.iterrows():
        for col in ['First Obs.', 'Last Obs.']:
            try:
                df.at[i, col] = pd.to_datetime(row[col], 
                                                format='%b %d, %Y')
            except ValueError:
                break
    
    return df

stations = get_stations()

def refresh_stations():
    global stations
    stations = get_stations()

def find_nearest_station(lat, lon):
    global stations
    location = np.array([lat, lon])
    locations = np.array(list(zip(stations['Latitude'], 
                                  stations['Longitude'])))
    dists = np.sum((locations - location) ** 2, axis=1)
    return stations.index[np.argmin(dists)]

def get_station(id):
    global stations
    if isinstance(id, tuple):
        lon, lat = id[0], id[1]
        id = find_nearest_station(lon, lat)
    if not isinstance(id, str):
        raise ValueError('`id` must be either <str> or <tuple>,'
                         ' got: {}'.format(id))
    return stations.loc[id]

__all__ = ['get_stations', 'refresh_stations',
           'find_nearest_station', 'get_station']