import tempfile
import unittest
from pathlib import Path
from dualspan.core import DualSpan
from dualspan.geometry import Monitor, Rect, Window

class FakeBackend:
    key = "fake"
    def __init__(self):
        self.rect = Rect(10, 10, 800, 600)
    def active_id(self): return "0x1"
    def get_window(self, wid): return Window("0x1", "Test", self.rect)
    def monitors(self): return [Monitor("A", Rect(0,0,1920,1080)),Monitor("B",Rect(1920,0,1920,1080))]
    def window_state(self,wid): return {"maximized":False}
    def move(self,wid,rect): self.rect = rect
    def restore_state(self,wid,state): pass

class CoreTests(unittest.TestCase):
    def test_span_restore(self):
        with tempfile.TemporaryDirectory() as d:
            b=FakeBackend()
            app=DualSpan(b, Path(d)/"state.json")
            rect,pair=app.span()
            self.assertEqual(rect.width,3840)
            self.assertEqual(pair,("A","B"))
            self.assertEqual(app.restore(),Rect(10,10,800,600))
    def test_cannot_span_twice(self):
        with tempfile.TemporaryDirectory() as d:
            app=DualSpan(FakeBackend(),Path(d)/"state.json")
            app.span()
            with self.assertRaises(RuntimeError): app.span()
