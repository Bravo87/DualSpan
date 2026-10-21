import unittest
from dualspan.backends.x11 import parse_xrandr, parse_wmctrl
class X11Tests(unittest.TestCase):
    def test_xrandr(self):
        text="HDMI-1 connected primary 1920x1080+0+0\nDP-1 connected 1920x1080+1920+0"
        self.assertEqual(len(parse_xrandr(text)),2)
    def test_window(self):
        text="0x12345 0 100 0 0 600 400 host Example Window"
        self.assertEqual(parse_wmctrl(text)[0].title,"Example Window")
