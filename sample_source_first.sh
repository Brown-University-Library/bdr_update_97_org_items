## USAGE: run this script from the `bdr_update_97_org_items` directory


## `u97__` envars are used by this `bdr_update_97_org_items` code --------
export U97__LOGLEVEL="DEBUG"
export U97__MODS_URL_PATTERN="url-to/storage/{PID}/MODS/"  # should match server for `UM__API_ROOT_URL` envar


## the `UM__` envars are used by the `update_mods_py_binary` -------------
export UM__API_AGENT="update_mods_script.py"
export UM__API_IDENTITY="THE:SHIB:IDENTITY"  # the shib-identity
export UM__API_ROOT_URL="api/private/url"  # the root api-url, used to build the full api-url
export UM__LOGLEVEL="DEBUG"
export UM__MESSAGE="adds indicator to MODS that this is an organization-item"


## venv ------------------------------------------------------------------
source ../env/bin/activate
