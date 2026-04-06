import ctypes
import os
import platform


def _load():
    system = platform.system()
    machine = platform.machine()

    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    lib_dir = os.path.join(pkg_dir, "lib")

    if system == "Linux":
        if machine in ("aarch64", "arm64"):
            name = "libflowex-arm64.so"
        else:
            name = "libflowex.so"
    elif system == "Darwin":
        name = "libflowex.dylib"
    elif system == "Windows":
        name = "libflowex.dll"
    else:
        raise OSError(f"Unsupported platform: {system}")

    path = os.path.join(lib_dir, name)
    lib = ctypes.CDLL(path)

    # FlowexInit(exchange *char) -> int
    lib.FlowexInit.argtypes = [ctypes.c_char_p]
    lib.FlowexInit.restype = ctypes.c_int

    # FlowexSubscribe(exchange *char, symbol *char) -> int
    lib.FlowexSubscribe.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.FlowexSubscribe.restype = ctypes.c_int

    # FlowexSubscribeBatch(exchange *char, symbols **char, count int) -> int
    lib.FlowexSubscribeBatch.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_char_p),
        ctypes.c_int,
    ]
    lib.FlowexSubscribeBatch.restype = ctypes.c_int

    # FlowexGetSnapshot(exchange *char, symbol *char) -> *char (caller must free)
    lib.FlowexGetSnapshot.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.FlowexGetSnapshot.restype = ctypes.c_void_p

    # FlowexGetSnapshots(exchange *char) -> *char (caller must free)
    lib.FlowexGetSnapshots.argtypes = [ctypes.c_char_p]
    lib.FlowexGetSnapshots.restype = ctypes.c_void_p

    # FlowexUnsubscribe(exchange *char, symbol *char) -> int
    lib.FlowexUnsubscribe.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.FlowexUnsubscribe.restype = ctypes.c_int

    # FlowexShutdown() -> void
    lib.FlowexShutdown.argtypes = []
    lib.FlowexShutdown.restype = None

    # FlowexFree(ptr *char) -> void
    lib.FlowexFree.argtypes = [ctypes.c_void_p]
    lib.FlowexFree.restype = None

    # FlowexGetStatus(exchange *char) -> *char (caller must free)
    lib.FlowexGetStatus.argtypes = [ctypes.c_char_p]
    lib.FlowexGetStatus.restype = ctypes.c_void_p

    # FlowexSubscribeCandle(exchange *char, symbol *char) -> int
    lib.FlowexSubscribeCandle.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.FlowexSubscribeCandle.restype = ctypes.c_int

    # FlowexSubscribeDepth(exchange *char, symbol *char) -> int
    lib.FlowexSubscribeDepth.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.FlowexSubscribeDepth.restype = ctypes.c_int

    # FlowexSubscribeTrade(exchange *char, symbol *char) -> int
    lib.FlowexSubscribeTrade.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    lib.FlowexSubscribeTrade.restype = ctypes.c_int

    # FlowexUnsubscribeStream(exchange *char, symbol *char, stream *char) -> int
    lib.FlowexUnsubscribeStream.argtypes = [
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p,
    ]
    lib.FlowexUnsubscribeStream.restype = ctypes.c_int

    # FlowexGetDepthHistory(exchange *char, symbol *char, count int) -> *char
    lib.FlowexGetDepthHistory.argtypes = [
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int,
    ]
    lib.FlowexGetDepthHistory.restype = ctypes.c_void_p

    # FlowexGetDepthByTimeRange(exchange, symbol, startMs, endMs) -> *char
    lib.FlowexGetDepthByTimeRange.argtypes = [
        ctypes.c_char_p, ctypes.c_char_p, ctypes.c_longlong, ctypes.c_longlong,
    ]
    lib.FlowexGetDepthByTimeRange.restype = ctypes.c_void_p

    return lib


lib = _load()
