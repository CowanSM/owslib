import os

def open_file(filepath, mode='r'):
    """Helper function to open files from within the tests directory"""
    return open(os.path.join(test_directory(), filepath), mode)

def test_directory():
    """Helper function to return path to the tests directory"""
    return os.path.dirname(__file__)

def scratch_directory():
    """Helper function to return path to the tests scratch directory"""
    return os.path.join(test_directory(), 'scratch')

def scratch_file(filename):
    """Helper function to return file path in the tests scratch directory"""
    return os.path.join(scratch_directory(), filename)