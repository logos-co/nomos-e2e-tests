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
    "error",
    "warn",
]

DATA_TO_DISPERSE = [
    "Hello World!",
    "1234567890",
    '{"key": "value"}',
    "这是一些中文",
    "🚀🌟✨",
    "Lorem ipsum dolor sit amet",
    "<html><body>Hello</body></html>",
    "0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF01234",
]
