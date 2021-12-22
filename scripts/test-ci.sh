#!/bin/bash

set -ex

coverage run -m pytest
coverage report --fail-under=75
