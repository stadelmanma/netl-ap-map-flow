"""
Handles testing of the bulk run module
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/06/10
#
"""
import os
import sys
#
module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
sys.path.insert(0,module_path)
#
from TestBulkRun import  TestBulkRun
from TestDataProcessing import  TestDataProcessing
from TestUnitConversion import  TestUnitConversion
from TestOpenFoamExport import  TestOpenFoamExport
#
test_classes = [
    TestBulkRun,
    TestDataProcessing,
    TestUnitConversion,
    TestOpenFoamExport
]
#
print('')
errors = False
for test_class in test_classes:
    test_class = test_class()
    errors = test_class.run_tests()
#
print('')
if (errors):
    print('Not all tests were sucessful')
else:
    print('All tests have passed')
