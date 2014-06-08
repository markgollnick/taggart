#!/bin/bash

# Initialization
argc=($#)
argv=($@)
arg0=${0#./} # Ensure no dot prefix
this=${0##*/} # Name of executing script
wdir=$([[ $0 == /* ]] && echo "${arg0%$this}" || echo "${PWD}/${arg0%$this}")
wdir=${wdir%/} # Ensure no trailing slash
pdir=${wdir%/*}

# Bootstrapper requirements
REQUIREMENTS="Python==2.7
setuptools==0.9.8
pip==1.4.1
virtualenv==1.10.1
virtualenvwrapper==4.3
"

# Display minimum requirements before bootstrapping an environment is possible
print_requirements() {
    echo "$1 not found."
    echo "Please ensure you have the following installed, at minimum:"
    for req in ${REQUIREMENTS[@]}; do echo $req; done
    exit 1
}

# Project name
project=${wdir##*/}

# virtualenvwrapper setup
export VIRTUALENVWRAPPER_PYTHON=$(which python)

# Sets the working directory for all virtualenvs
export WORKON_HOME=$HOME/.virtualenvs

# Sources the virtualenvwrapper so all the commands are availabe in the shell
export VIRTUALENVWRAPPER=$(which virtualenvwrapper.sh)

# Detect requirements
if [ "$VIRTUALENVWRAPPER_PYTHON" == "" ]; then
    print_requirements "python"
elif [ "$VIRTUALENVWRAPPER" == "" ]; then
    print_requirements "virtualenvwrapper"
fi

# Set up a virtual environment for this project
source "$VIRTUALENVWRAPPER"
if [ ! -e "$WORKON_HOME/$project.venv" ]; then
    mkvirtualenv $project.venv -a $wdir
else
    workon $project.venv
fi
pip install -r requirements_dev.txt
