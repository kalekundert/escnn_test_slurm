#!/usr/bin/env python3

"""\
Usage:
    assign_order.py <dir>

Arguments:
    <dir>
        A directory containing the output files produced by `run_tests`.
"""

import docopt
import json

from check_results import load_test_results
from pathlib import Path

def record_order(results):
    times = {
            name: result.time_s
            for name, result in results.items()
    }
    with open('test_order.json', 'w') as f:
        json.dump(times, f)

if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    results = load_test_results(Path(args['<dir>']))
    record_order(results)
