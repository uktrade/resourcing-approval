#!/bin/bash

set -ex

coverage run -m pytest
coverage report --sort=cover --fail-under=88
