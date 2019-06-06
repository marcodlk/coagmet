#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `raw_data` module."""

import pytest

import pandas as pd

from coagmet.raw_data import RawData


def test_get_raw_data():
    hot01_raw = RawData('HOT01')
    df = hot01_raw.get('2019-01-01')
    assert len(df) == 1
    df = hot01_raw.get('2019-01-01', '2019-01-01')
    assert len(df) == 1
    df = hot01_raw.get('2019-01-01', '2019-01-02')
    assert len(df) == 2