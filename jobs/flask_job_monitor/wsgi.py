import os
import random
import string
import sys

sys.path.insert(0, os.path.dirname(__file__))
from job_monitor import app as application
application.secret_key = ''.join(random.choice(string.ascii_uppercase) for _ in range(32))
