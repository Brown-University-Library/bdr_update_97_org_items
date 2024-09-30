import logging, pathlib


log = logging.getLogger( __name__ )


## helper functions -------------------------------------------------


def load_pids( pid_full_fpath: pathlib.Path ) -> list:
    """
    Load pids from file.
    """
    pids = []
    with open( pid_full_fpath, 'r' ) as f:
        for line in f:
            line = line.strip()
            if line:
                pids.append( line )
    log.debug( f'pids, ```{pids}```' )
    return pids


## manager function -------------------------------------------------


def manage_update( pid_full_fpath: pathlib.Path ):
    """
    Manages processing of mods-update.
    Called by: cli_start.py
    """
    ## get list of pids from file -----------------------------------
    pids: list = load_pids( pid_full_fpath )
    ## loop over pids -----------------------------------------------
    for pid in pids:
        assert type(pid) == int
        ## get mods -------------------------------------------------
        mods = get_mods( pid )
        ## update mods ----------------------------------------------
        updated_mods = update_mods( mods )
        ## save mods ------------------------------------------------
        save_mods( pid, updated_mods )
    pass


## helpers ----------------------------------------------------------


