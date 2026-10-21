"""Windows 10/11 window geometry backend via Win32 ctypes."""
import ctypes
import os
from ctypes import wintypes
from dualspan.geometry import Monitor, Rect, Window

class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG),
                ("right", wintypes.LONG), ("bottom", wintypes.LONG)]

class MONITORINFOEXW(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", RECT),
                ("rcWork", RECT), ("dwFlags", wintypes.DWORD),
                ("szDevice", wintypes.WCHAR * 32)]

def rect_to_geometry(r):
    return Rect(r.left, r.top, r.right-r.left, r.bottom-r.top)

class WindowsBackend:
    key = "windows"
    def __init__(self):
        if os.name != "nt": raise RuntimeError("Windows backend requires Windows 10 or 11")
        self.api = ctypes.WinDLL("user32", use_last_error=True)
        try: ctypes.WinDLL("shcore").SetProcessDpiAwareness(2)
        except (OSError, AttributeError):
            try: self.api.SetProcessDPIAware()
            except (OSError, AttributeError): pass
        self.api.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
        self.api.GetWindowRect.restype = wintypes.BOOL
        self.api.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
        self.api.SetWindowPos.restype = wintypes.BOOL
        self.api.GetForegroundWindow.restype = wintypes.HWND
        self.api.IsWindow.argtypes = [wintypes.HWND]
        self.api.IsWindow.restype = wintypes.BOOL
        self.api.IsZoomed.argtypes = [wintypes.HWND]
        self.api.IsZoomed.restype = wintypes.BOOL
        self.api.IsWindowVisible.argtypes = [wintypes.HWND]
        self.api.IsWindowVisible.restype = wintypes.BOOL
        self.api.GetWindowTextLengthW.argtypes = [wintypes.HWND]
        self.api.GetWindowTextLengthW.restype = ctypes.c_int
        self.api.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        self.api.GetWindowTextW.restype = ctypes.c_int
        self.api.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        self.api.ShowWindow.restype = wintypes.BOOL
    def monitors(self):
        result = []
        cb = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HANDLE, wintypes.HDC, ctypes.POINTER(RECT), wintypes.LPARAM)
        self.api.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MONITORINFOEXW)]
        self.api.GetMonitorInfoW.restype = wintypes.BOOL
        self.api.EnumDisplayMonitors.argtypes = [wintypes.HDC, ctypes.POINTER(RECT), cb, wintypes.LPARAM]
        self.api.EnumDisplayMonitors.restype = wintypes.BOOL
        def visit(handle, _dc, _rect, _data):
            info = MONITORINFOEXW()
            info.cbSize = ctypes.sizeof(info)
            if self.api.GetMonitorInfoW(handle, ctypes.byref(info)):
                result.append(Monitor(info.szDevice, rect_to_geometry(info.rcMonitor)))
            return True
        callback = cb(visit)
        if not self.api.EnumDisplayMonitors(None, None, callback, 0):
            raise RuntimeError("Could not enumerate monitors")
        return result
    def windows(self):
        result=[]
        cb=ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        self.api.EnumWindows.argtypes=[cb,wintypes.LPARAM]
        self.api.EnumWindows.restype=wintypes.BOOL
        self.api.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
        def visit(hwnd, _data):
            if not self.api.IsWindowVisible(hwnd): return True
            length=self.api.GetWindowTextLengthW(hwnd)
            if not length: return True
            proc=wintypes.DWORD()
            self.api.GetWindowThreadProcessId(hwnd,ctypes.byref(proc))
            if proc.value == os.getpid(): return True
            buf=ctypes.create_unicode_buffer(length+1)
            self.api.GetWindowTextW(hwnd,buf,len(buf))
            if not buf.value.strip(): return True
            try: result.append(Window(hex(hwnd),buf.value,self._rect(hwnd)))
            except RuntimeError: pass
            return True
        callback=cb(visit)
        if not self.api.EnumWindows(callback,0): raise RuntimeError("Cannot enumerate windows")
        return result
    def active_id(self):
        hwnd=self.api.GetForegroundWindow()
        if not hwnd: raise RuntimeError("No foreground application")
        return hex(hwnd)
    def _rect(self,hwnd):
        r=RECT()
        if not self.api.GetWindowRect(hwnd,ctypes.byref(r)): raise RuntimeError("Cannot read window geometry")
        return rect_to_geometry(r)
    def get_window(self,wid):
        hwnd=int(wid,16)
        if not self.api.IsWindow(hwnd): raise RuntimeError("Window no longer exists")
        length=self.api.GetWindowTextLengthW(hwnd)
        buf=ctypes.create_unicode_buffer(length+1)
        self.api.GetWindowTextW(hwnd,buf,len(buf))
        return Window(hex(hwnd),buf.value or "Untitled window",self._rect(hwnd))
    def window_state(self,wid):
        return {"maximized":bool(self.api.IsZoomed(int(wid,16)))}
    def move(self,wid,rect):
        hwnd=int(wid,16)
        if not self.api.IsWindow(hwnd): raise RuntimeError("Window no longer exists")
        self.api.ShowWindow(hwnd,9)
        if not self.api.SetWindowPos(hwnd,None,rect.x,rect.y,rect.width,rect.height,0x0004|0x0010):
            raise RuntimeError("Windows refused to resize this window")
    def restore_state(self,wid,state):
        if state.get("maximized"): self.api.ShowWindow(int(wid,16),3)
