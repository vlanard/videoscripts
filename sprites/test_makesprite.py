__author__ = 'vlanard'

import unittest
import makesprites as mks

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_makevtt(self):
        pass

    def test_get_grid_coordinates(self):
        w = 100
        h = 50
        self.assertEqual("0,0,%d,%d" % (w,h),mks.get_grid_coordinates(1,1,w,h) )
        self.assertEqual("0,0,%d,%d" % (w,h),mks.get_grid_coordinates(1,2,w,h) )
        self.assertEqual("0,0,%d,%d" % (w,h),mks.get_grid_coordinates(1,3,w,h) )
        self.assertEqual("0,0,%d,%d" % (w,h),mks.get_grid_coordinates(1,4,w,h) )
        self.assertEqual("0,0,%d,%d" % (w,h),mks.get_grid_coordinates(1,5,w,h) )
        self.assertEqual("100,0,%d,%d" % (w,h),mks.get_grid_coordinates(2,2,w,h) )
        self.assertEqual("0,50,%d,%d" % (w,h),mks.get_grid_coordinates(3,2,w,h) )
        self.assertEqual("100,50,%d,%d" % (w,h),mks.get_grid_coordinates(4,2,w,h) )
        self.assertEqual("100,0,%d,%d" % (w,h),mks.get_grid_coordinates(2,3,w,h) )
        self.assertEqual("200,0,%d,%d" % (w,h),mks.get_grid_coordinates(3,3,w,h) )
        self.assertEqual("0,50,%d,%d" % (w,h),mks.get_grid_coordinates(4,3,w,h) )
        self.assertEqual("100,50,%d,%d" % (w,h),mks.get_grid_coordinates(5,3,w,h) )
        self.assertEqual("200,50,%d,%d" % (w,h),mks.get_grid_coordinates(6,3,w,h) )
        self.assertEqual("0,100,%d,%d" % (w,h),mks.get_grid_coordinates(7,3,w,h) )
        self.assertEqual("100,100,%d,%d" % (w,h),mks.get_grid_coordinates(8,3,w,h) )
        self.assertEqual("200,100,%d,%d" % (w,h),mks.get_grid_coordinates(9,3,w,h) )

    def test_get_time_str(self):
        self.assertEqual("00:00:00.000", mks.get_time_str(0))
        self.assertEqual("00:00:05.000", mks.get_time_str(5))
        self.assertEqual("00:00:45.000", mks.get_time_str(45))
        self.assertEqual("00:02:25.000", mks.get_time_str(145))
        seventymin = 60*70
        self.assertEqual("01:10:00.000", mks.get_time_str(seventymin))
        seventyminten = 60*70 +10

        self.assertEqual("01:10:00.000", mks.get_time_str(seventyminten,adjust=-10))
        self.assertEqual("00:00:00.000", mks.get_time_str(0,adjust=-10))
        self.assertEqual("00:00:00.000", mks.get_time_str(5,adjust=-10))
        self.assertEqual("01:10:10.000", mks.get_time_str(seventyminten,adjust=0))
        self.assertEqual("01:10:20.000", mks.get_time_str(seventyminten,adjust=10))
        self.assertEqual("00:00:10.000", mks.get_time_str(0,adjust=10))
        self.assertEqual("00:00:15.000", mks.get_time_str(5,adjust=10))


if __name__ == '__main__':
    unittest.main()
