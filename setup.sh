#!/usr/bin/env bash
IMD_HOME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $IMD_HOME
export IMD_HOME
export PATH=$IMD_HOME:$PATH
chmod 777 demo-convert.py
