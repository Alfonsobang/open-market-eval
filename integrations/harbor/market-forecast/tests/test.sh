#!/bin/sh
set -eu
python -m unittest discover -s /tests -p 'test_*.py' -v
