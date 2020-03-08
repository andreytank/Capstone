#!/usr/bin/env python
"""
model tests
"""


import unittest,os,sys,random
## import model specific functions and variables
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(THIS_DIR)
sys.path.append(PARENT_DIR)
import time,os,re,csv,sys,uuid,joblib
from datetime import date
sys.path.append(PARENT_DIR)
from solution_guidance.example_logging import _update_predict_log

class LoggingTest(unittest.TestCase):
    """
    test the essential functionality
    """
        
    def test_01_train(self):
        """
        test logging
        """
        ## create log
        time_start = time.time()
        target_date = "{}-{}-{}".format("9999","12","31")
        m, s = divmod(time.time()-time_start, 60)
        h, m = divmod(m, 60)
        runtime = "%03d:%02d:%02d"%(h, m, s)
        _update_predict_log('logtest_country',0,0,target_date,runtime, 0.0, test=True)
        #check log
        today = date.today()
        logdir = os.path.join(PARENT_DIR,"static","logs")
        logfile = os.path.join(logdir, "example-predict-{}-{}.log.csv".format(today.year, today.month))
        logs = [f for f in os.listdir(logdir) if re.search("example-predict-{}-{}.log.csv".format(today.year, today.month),f)]
        self.assertTrue(len(logs) != 0)

        
### Run the tests
if __name__ == '__main__':
    unittest.main()
