#!/bin/bash

set -e
gunicorn -b 0.0.0.0:8000 modularhistory.wsgi:application
