"""
- Reads command-line argument to file containing list of PIDs to update.
- Validate that file exists and is readable.
- Calls update_orgs/manage_update.py
"""

import argparse, logging, os, pathlib
from update_org_mods import manage_update


## setup logging ----------------------------------------------------
LOGLEVEL: str = os.environ.get( 'U97__LOGLEVEL', 'DEBUG' )  # 'DEBUG' or 'INFO' (namespacing for "Update 97 org-items")
lglvldct = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO }
logging.basicConfig(
    level=lglvldct[LOGLEVEL],  # assigns the level-object to the level-key loaded from the envar
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger( __name__ )


def validate_pid_file( pid_full_fpath: pathlib.Path ):
    """
    Validate that the given file exists and is readable.
    Called by: dundermain.
    """
    validity = False
    if pid_full_fpath.exists() and pid_full_fpath.is_file() and os.access( pid_full_fpath, os.R_OK ):
        validity = True
    log.debug( f'validity: {validity}' )
    return validity


if __name__ == '__main__':
    ## parse command-line arguments ---------------------------------
    parser = argparse.ArgumentParser( description='Update BDR organization items.' )
    parser.add_argument( '--pid_filepath', type=pathlib.Path, help='File containing list of PIDs to update.' )
    args = parser.parse_args()
    pid_full_fpath: pathlib.Path = args.pid_filepath.resolve()
    log.debug( f'pid_full_fpath: ``{pid_full_fpath}``' )
    ## validate pid_file --------------------------------------------
    if validate_pid_file( pid_full_fpath ):
        manage_update( pid_full_fpath )
    else:
        print( f'Error: ``{pid_full_fpath}`` is not a valid file or is not readable.' )
