Example for ws4py (0.3.3) with CherryPy (3.2.4).

Because ws4py doesn't support subprotocols currently, whether msgpack is used or not is decided by the format of the first message; if it is binary, then msgpack is used, otherwise JSON is used.

