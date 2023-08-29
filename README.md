Run the ESCNN test suite on a SLURM cluster
===========================================

Usage
-----
Create a virtual environment named `venv` in the root of an ESCNN repository:
```
$ cd /path/to/escnn
$ python -m venv venv
$ . venv/bin/activate
```
Install ESCNN:
```
$ pip install .
```
Submit the tests:
```
$ cd /path/to/escnn_test_slurm
$ ./run_tests /path/to/escnn
```
Wait for the tests to complete.  The `run_tests` command sets a 4h runtime
limit, but not all of the tests will finish within that time.  The results will
appear in a directory named after the current commit in the ESCNN repository.

View the results:
```
$ ./check_results.py <output dir>
```

Compare the results from two different commits:
```
$ ./check_results.py <output dir> -x <reference output dir>
```

