import ctypes


class ControllerStatus(ctypes.BigEndianStructure):
    """
    unsigned int ready : 1;
    unsigned int alarm : 1;
    unsigned int run_index : 1;
    unsigned int run_sync : 1;
    unsigned int unused : 12;
    """
    pack_format = ">H"
    _fields_ = [
        ("unused", ctypes.c_uint32, 12),
        ("run_sync", ctypes.c_uint32, 1),
        ("run_index", ctypes.c_uint32, 1),
        ("alarm", ctypes.c_uint32, 1),
        ("ready", ctypes.c_uint32, 1),
    ]


class ControllerControl(ctypes.BigEndianStructure):
    """
    unsigned int reset : 1;
    unsigned int emergency : 1;
    unsigned int enable : 1;
    unsigned int request_sync_init: 1;
    unsigned int unused : 12;
    """
    pack_format = ">H"
    _fields_ = [
        ("unused", ctypes.c_uint32, 12),
        ("request_sync_init", ctypes.c_uint32, 1),
        ("enable", ctypes.c_uint32, 1),
        ("emergency", ctypes.c_uint32, 1),
        ("reset", ctypes.c_uint32, 1),
    ]
