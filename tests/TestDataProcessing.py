"""
Handles testing of the data processing module
#
Written By: Matthew Stadelman
Date Written: 2016/06/09
Last Modifed: 2016/06/10
#
"""
#
class TestDataProcessing:
    r"""
    Executes a set of functions to handle testing of the data processing
    routines
    """
    def __init__(self):
        pass

    def run_tests(self):
        r"""
        Loops through supplied testing functions
        """
        #
        test_functions = [
        ]
        #
        errors = False
        for func in test_functions:
            try:
                func()
            except Exception as err:
                errors = True
                print('*** Error - :'+self.__class__.__name__+':', err, ' ***')
        #
        return errors
#
print('Testing data processing')