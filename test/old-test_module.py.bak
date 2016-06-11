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
    TestUnitConversion,
    TestDataProcessing,
    TestBulkRun,
    TestOpenFoamExport
]
#
print('')
errors = False
for test_class in test_classes:
    test_class = test_class()
    error = test_class.run_tests()
    if (error):
        print(test_class.__class__.__name__+' has failed')
        errors = True
#
print('')
if not errors:
    print('All tests have passed')
