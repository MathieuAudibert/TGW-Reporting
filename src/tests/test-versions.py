import unittest
import sys
import subprocess
import boto3

class TestVersions(unittest.TestCase):

    def test_python_version(self):
        """
        Checks python version
        """
        python_version = sys.version_info
        self.assertGreaterEqual(python_version.major, 3)
        
        if python_version.major == 3:
            self.assertGreaterEqual(python_version.minor, 12)

    def test_boto3_version(self):
        """
        Checks boto3 version
        """
        boto3_version = boto3.__version__
        major, minor, *rest = map(int, boto3_version.split('.'))
        self.assertGreaterEqual(major, 1)
        
        if major == 1:
            self.assertGreaterEqual(minor, 34)

    def test_r_version(self):
        """
        Checks R version
        """
        try:
            result = subprocess.run(['R', '--version'], capture_output=True, text=True)
            version_line = result.stdout.split('\n')[0]
            version_str = version_line.split(' ')[2]
            major, minor, *rest = map(int, version_str.split('.'))
            
            self.assertGreaterEqual(major, 4)
            if major == 4:
                self.assertGreaterEqual(minor, 2)
        except Exception as e:
            self.fail(f"Failed to get R version: {str(e)}")

if __name__ == '__main__':
    unittest.main()
