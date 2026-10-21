import unittest
from dualspan.geometry import Rect, Monitor, union, selection

class GeometryTests(unittest.TestCase):
    def test_union_adjacent(self):
        self.assertEqual(union(Rect(0,0,1920,1080),Rect(1920,0,1920,1080)),Rect(0,0,3840,1080))
    def test_union_negative_offset(self):
        self.assertEqual(union(Rect(-1920,0,1920,1080),Rect(0,0,1920,1080)),Rect(-1920,0,3840,1080))
    def test_two_required(self):
        with self.assertRaises(ValueError): selection([Monitor("one",Rect(0,0,1,1))],Rect(0,0,1,1))
    def test_explicit_pair(self):
        monitors=[Monitor(str(i),Rect(i*100,0,100,100)) for i in range(3)]
        a,b=selection(monitors,Rect(0,0,100,100),(0,2))
        self.assertEqual((a.name,b.name),("0","2"))
