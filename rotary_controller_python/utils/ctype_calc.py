import ctypes


def uint32_subtract_to_int32(a, b):
    return ctypes.c_int32(ctypes.c_uint32(a).value - ctypes.c_uint32(b).value).value
