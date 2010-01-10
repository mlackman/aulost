#!/usr/bin/python2.5
import os 
import unittest

def is_test_file(filename):
    return filename.startswith('test_') and filename.endswith('.py') 

if __name__ == '__main__':
    files = os.listdir(os.path.curdir)
    test_files = filter(lambda filename: is_test_file(filename), files)
    # Strip the '.py" from the filename
    test_modules = map(lambda test_file: test_file[:-3], test_files) 

    testloader = unittest.TestLoader()
    testsuites = testloader.loadTestsFromNames(test_modules)
         
    all_successfull = True
    for suite in testsuites:
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            all_successfull = False   

    if all_successfull:
        print 'All TESTS OK'
    else:
        print 'Some test(s) failed'
