# Copyright (c) 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

from pathlib import Path
import sys


CAPACITY_RESERVATION_DIRECTORY = Path(__file__).resolve().parents[1]
if str(CAPACITY_RESERVATION_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(CAPACITY_RESERVATION_DIRECTORY))
