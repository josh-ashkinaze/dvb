#!/bin/bash

python3 -m venv venv

venv/bin/pip install -r requirements.txt

source venv/bin/activate

echo "Virtual environment setup complete and activated!"