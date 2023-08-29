#!/usr/bin/env python3

"""\
Usage:
    check_results <dir> [-x <dir>]

Arguments:
    <dir>
        A directory containing the output files produced by `run_tests`.

Options:
    -x --expected <dir>
        A directory containing a set of expected (or reference) results.  This
        will be used to classify tests as XFAIL or XPASS.
"""

import docopt
import re

from pathlib import Path
from dataclasses import dataclass
from collections import Counter
from itertools import groupby
from datetime import timedelta
from typing import Optional

@dataclass
class TestResult:
    status: str
    message: Optional[str]
    time_s: float

def load_test_results(path):
    return {
            p.stem: parse_test_result(p)
            for p in path.glob('*.unittest')
    }

def parse_test_result(path):
    with open(path) as f:
        lines = f.readlines()

    if lines[-1].startswith('QUEUED'):
        status = 'queued'
    elif lines[-1].startswith('OK'):
        status = 'pass'
    elif lines[-1].startswith('FAIL'):
        status = 'fail'
    else:
        status = 'unknown'

    if status in ('queued', 'pass'):
        message = None
    else:
        j = 0
        for i, line in enumerate(lines):
            if line.startswith('  File'):
                j = i
        message = lines[j+2].strip()

        heterogeneous = [
                "AssertionError: False is not true",
                "AssertionError: The error found during equivariance check with element",
                "RuntimeError: Found no NVIDIA driver on your system",
        ]
        for prefix in heterogeneous:
            if message.startswith(prefix):
                message = f"{prefix}..."

    if status == 'queued':
        time_s = 0
    else:
        m = re.match(r'Ran 1 test in (\d+\.\d+)s', lines[-3])
        time_s = float(m.group(1))

    return TestResult(
            status=status,
            message=message,
            time_s=time_s,
    )

def format_results(results, expected):
    time_s = sum(x.time_s for x in results.values())
    print(f"RUNTIME: {timedelta(seconds=int(time_s))}", end='\n\n')

    if expected:
        for k in results:
            if k not in expected:
                continue

            if results[k].status == 'pass' and expected[k].status == 'fail':
                results[k].status = 'xpass'
            if results[k].status == 'fail' and expected[k].status == 'fail' \
                    and results[k].message == expected[k].message:
                results[k].status = 'xfail'

    counts = Counter()
    for result in results.values():
        counts[result.status] += 1

    print(f"TOTAL: {counts.total():4d}")
    print(f"PASS:  {counts.pop('pass', 0):4d}")
    print(f"FAIL:  {counts.pop('fail', 0):4d}")

    if expected:
        print(f"XPASS: {counts.pop('xpass', 0):4d}")
        print(f"XFAIL: {counts.pop('xfail', 0):4d}")

    print(f"QUEUE: {counts.pop('queued', 0):4d}")
    
    if counts:
        print(f"OTHER: {counts.total():4d}")

    print()

    def by_message(item):
        _, result = item
        return result.message

    failures = [
            (name, result)
            for name, result in results.items()
            if result.status == 'fail'
    ]
    failures = sorted(failures, key=by_message)

    if failures:
        print("FAILURES:")

        for message, items in groupby(failures, key=by_message):
            print(f"  {message}")
            for name, result in items:
                print(f"      {name}")
            print()

if __name__ == '__main__':
    args = docopt.docopt(__doc__)

    results = load_test_results(Path(args['<dir>']))

    if p := args['--expected']:
        expected = load_test_results(Path(p))
    else:
        expected = None

    format_results(results, expected)
