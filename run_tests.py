#!/usr/bin/env python3

import unittest
import sys, os, io, json

from more_itertools import collapse, distribute, nth
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

# Usage:
# Provide array parameters and the path to an escnn repository via environment
# variables.  Provide an output directory as a command-line argument.  For
# example:
#
#     ESCNN_REPO=~/sandbox/escnn SLURM_ARRAY_TASK_COUNT=100 SLURM_ARRAY_TASK_ID=0 python run_tests.py out

def load_test_order():
    order_json = Path('__file__').parent / 'test_order.json'

    if not order_json.exists():
        return {}
    
    with order_json.open() as f:
        return json.load(f)

def by_order(test):
    name = test.id()
    return test_order.get(name, 0), name

def prepare_test(test, out_dir):
    (out_dir / f'{test.id()}.unittest').write_text('QUEUED\n')

def run_test(test):
    testout = io.StringIO()
    stdout = io.StringIO()
    stderr = io.StringIO()

    runner = unittest.TextTestRunner(testout)

    with redirect_stdout(stdout), redirect_stderr(stderr):
        runner.run(test)

    return testout.getvalue(), stdout.getvalue(), stderr.getvalue()

def record_test(test, out_dir, testout, stdout, stderr):
    (out_dir / f'{test.id()}.unittest').write_text(testout)
    (out_dir / f'{test.id()}.stdout').write_text(stdout)
    (out_dir / f'{test.id()}.stderr').write_text(stderr)

out_dir = Path(sys.argv[1])
num_workers = int(os.environ['SLURM_ARRAY_TASK_COUNT'])
worker_id = int(os.environ['SLURM_ARRAY_TASK_ID'])
test_dir = Path(os.environ['ESCNN_REPO']) / 'test'
test_order = load_test_order()

# Might eventually make sense to sort this list by some estimate of how long 
# each test will take, so keep all the task about the same running time.
loader = unittest.TestLoader()
all_tests = collapse(loader.discover(test_dir))
all_tests = sorted(all_tests, key=by_order)
my_tests = list(nth(distribute(num_workers, all_tests), worker_id))

for test in my_tests:
    prepare_test(test, out_dir)

for test in my_tests:
    out = run_test(test)
    record_test(test, out_dir, *out)

