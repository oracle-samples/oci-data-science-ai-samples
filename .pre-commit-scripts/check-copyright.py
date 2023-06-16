#!/usr/bin/env python

# Copyright (c) 2023 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

import datetime
import os
import sys

CURRENT_YEAR = datetime.date.today().year

### At the beginning of next year line has to be added in this list:
PUBLISHED_LAST_EDITED_YEARS = [
    f"Copyright (c) 2020, {CURRENT_YEAR} Oracle and/or its affiliates",
    f"Copyright (c) 2021, {CURRENT_YEAR} Oracle and/or its affiliates",
    f"Copyright (c) 2022, {CURRENT_YEAR} Oracle and/or its affiliates",
    f"Copyright (c) {CURRENT_YEAR} Oracle and/or its affiliates",
]

LICENSE_STATEMENTS = [
    "Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/"
]

def main(filenames) -> int:
    phrases = LICENSE_STATEMENTS
    years = PUBLISHED_LAST_EDITED_YEARS
    retcode = 0
    for filename in filenames:
        if not os.path.basename(filename).startswith("."):
            with open(filename) as inputfile:
                content = inputfile.read()
                if not any(x in content for x in years):
                    print(f"{filename}: Year published or year last edited not correct.")
                    retcode = 1
                    break
                for p in phrases:
                    if p not in content:
                        print(f"{filename}: Copyright text missing or incomplete.")
                        retcode = 1
                        break

    sys.exit(retcode)


if __name__ == "__main__":
    filenames = sys.argv
    main(filenames)
