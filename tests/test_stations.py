#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for :mod:`~coagmet.stations` module."""

import pytest

import pandas as pd

from coagmet.stations import Stations 


def test_get_station():
    station_id = 'HOT01'
    stations = Stations()
    stations_df = stations.get()
    station = stations.get_station(station_id)
    assert isinstance(station, pd.Series)
    expect_fields = ['Station Name',
                     'Location',
                     'Latitude',
                     'Longitude',
                     'Elev. (ft)',
                     'First Obs.',
                     'Last Obs.',
                     'Irrigation Type']
    actual_fields = station.index.values.tolist()
    assert expect_fields == actual_fields
    assert stations_df.loc[station_id].all() == station.all()