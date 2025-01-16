from time import time
from datetime import datetime, timedelta

LOG_ERROR_KEYWORDS = [
    "crash",
    "fatal",
    "panic",
    "abort",
    "segfault",
    "corrupt",
    "terminated",
    "unhandled",
    "stacktrace",
    "deadlock",
    "SIGSEGV",
    "SIGABRT",
    "stack overflow",
    "index out of bounds",
    "nil pointer dereference",
    "goroutine exit",
    "nil pointer",
    "runtime error",
    "goexit",
    "race condition",
    "double free",
]
