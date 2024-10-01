#!/bin/bash

## USAGE: run this script from the outer "stuff" directory


## check current directory -----------------------------------------------
current_dir=$(basename "$PWD")
if [[ "$current_dir" == *stuff || "$current_dir" == *outer ]]; then
    echo "Running script in a valid directory."
else
    echo "Error: This script must be run from a directory ending in 'stuff' or 'outer'."
    exit 1
fi


## `u97__` envars are used by this `bdr_update_97_org_items` code --------
export U97__LOGLEVEL="DEBUG"
export U97__MODS_URL_PATTERN="url-to/storage/{PID}/MODS/"  # should match server for `UM__API_ROOT_URL` envar


## the `UM__` envars are used by the `update_mods_py_binary` -------------
export UM__API_AGENT="update_mods_script.py"
export UM__API_IDENTITY="THE:SHIB:IDENTITY"     # the shib-identity
export UM__API_ROOT_URL="api/private/url"       # the root api-url, used to build the full api-url
export UM__LOGLEVEL="DEBUG"
export UM__MESSAGE="adds indicator to MODS that this is an organization-item"


## venv ------------------------------------------------------------------
source ../env/bin/activate
