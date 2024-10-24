import unittest
from hw1part1 import *
import pandas as pd
import numpy as np


class TestMinute(unittest.TestCase):
	def test_minute(self):
		ser = pd.Series([1030.0, 1259.0, np.nan, 2475], dtype='float64')
		self.assertTrue(extract_mins(ser).equals(pd.Series([30, 59, np.nan, np.nan], dtype='float64')))


class TestMinOfDay(unittest.TestCase):
	def test_minofday(self):
		ser = pd.Series(['13:03:00', '12:00:00', '24:00:00'])
		self.assertTrue(convert_to_minofday(ser).equals(pd.Series([783, 720, np.nan], dtype='float64')))


class TestAssignedScheduledTimes(unittest.TestCase):   
    def test_assigned_scheduled_times(self):
        arrival_times = pd.Series([745, 815, 900, 935, 1000])  
        scheduled_times = pd.Series([700, 750, 800, 900, 940])
        df = pd.DataFrame({
            'Arrival Times': [745, 815, 900, 935, 1000],
            'Scheduled Times': [750, 800, 900, 940, 940]  
        })
        pd.testing.assert_frame_equal(assigned_scheduled_times(arrival_times, scheduled_times), df)



class TestTimeDiff(unittest.TestCase):
	def test_calc_delay_one(self):
		sched = pd.Series([1415, 720, 450, 1730, 500, np.nan], dtype='float64')
		actual = pd.Series([1443, 810, 513, 1734, 450, np.nan], dtype='float64')
		self.assertTrue(calc_delay(pd.concat([sched, actual], axis=1)).equals(pd.Series([28, 50, 23, 4, -10, np.nan], dtype='float64')), msg = "calc_delay() output does not match the correct output!")
