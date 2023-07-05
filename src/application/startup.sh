#!/bin/bash

# Run import_pipeline.py
python3 import-script/import_pipeline.py

# Start cron (assuming the cron service is installed and configured)
service cron start

# Run app.py
python3 app.py
