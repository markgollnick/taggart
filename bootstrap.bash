#!/bin/bash

# Initialization
ARG0=${0#./}
THIS=${0##*/}
WDIR=$([[ $0 == /* ]] && echo "${ARG0%$THIS}" || echo "$PWD/${ARG0%$THIS}")
WDIR=${WDIR%/}


# Script entry point
__bootstrap_main() {
    IFS=$'\n'
    argc=($#)
    argv=($@)

    # Usage information
    if [ "${argv[0]}" == "--help" -o "${argv[0]}" == "-h" ]; then
        echo "Usage: $THIS [virtualenv_name]"
        return 0
    fi

    # Sets the working directory for all virtualenvs if it is not already set
    if [ "$WORKON_HOME" == "" ]; then
        export WORKON_HOME="$HOME/.virtualenvs"
    fi
    export VIRTUALENVWRAPPER_SCRIPT=$(which virtualenvwrapper.sh)

    # Sources virtualenvwrapper so all the commands are available in the shell
    if [ "$VIRTUALENVWRAPPER_SCRIPT" == "" ]; then
        echo "virtualenvwrapper not found."
        echo "Please pip install virtualenv and virtualenvwrapper"
        return 1
    fi
    source "$VIRTUALENVWRAPPER_SCRIPT"

    # Set up or activate a virtual environment for this project
    venv=$([[ "${argv[0]}" != "" ]] && echo "${argv[0]}" || echo "${WDIR##*/}")
    if [ ! -e "$WORKON_HOME/$venv" ]; then
        mkvirtualenv "$venv" -a "$WDIR"
    else
        workon "$venv"
    fi
    if [ "$VIRTUAL_ENV" == "" ]; then
        echo "Could not bootstrap virtual environment, quitting..."
        return 1
    fi

    # Install production and development requirements if present
    for requirements in $WDIR/requirements{_dev,}.txt; do
        if [ -e "$requirements" ]; then
            pip install -r "$requirements"
        fi
    done

    echo "Bootstrap successful. Type 'workon $venv' to begin work."
    return 0
}


__bootstrap_main "$@"
