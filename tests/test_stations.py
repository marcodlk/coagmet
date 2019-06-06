#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `stations` module."""

import pytest

import pandas as pd

from coagmet.stations import get_station, find_nearest_station


def test_get_station():
    station = get_station('HOT01')
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