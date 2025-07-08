import os
import sys

# 非顶层包不加这个会import协议失败
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "api/protocol")))
from .follow_channel import follow_channel  # noqa: F401

from .pusher import *  # noqa: F401
