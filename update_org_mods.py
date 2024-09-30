import json, logging, pathlib
import httpx


log = logging.getLogger( __name__ )

MODS_URL_PATTERN = 'https://repository.library.brown.edu/storage/{PID}/MODS/'


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


def load_tracker( pid_full_fpath: pathlib.Path ) -> dict:
    """
    Load tracker.
    Assumes tracker is in same directory as pid-file.
    """
    tracker_full_fpath = pid_full_fpath.parent.joinpath( 'tracker.json' )
    tracker = {}
    if tracker_full_fpath.exists():
        with open( tracker_full_fpath, 'r' ) as f:
            tracker = json.loads( f.read() )
    log.debug( f'tracker, ```{tracker}```' )
    return tracker


def check_if_pid_was_processed( pid: str, tracker: dict ) -> str:
    """
    Check if pid was processed.
    """
    status = tracker.get( pid, 'not_done' )
    log.debug( f'pid, ``{pid}``; status, ``{status}``' )
    return status


def get_mods( pid: str ) -> str:
    """
    Get mods using the constant.
    """
    mods_url: str = MODS_URL_PATTERN.format( PID=pid )
    log.debug( f'mods_url, ```{mods_url}```' )
    resp: httpx.Response = httpx.get( mods_url )
    mods: str = resp.content.decode( 'utf-8' )  # explicitly declare utf-8
    return mods


## manager function -------------------------------------------------


def manage_update( pid_full_fpath: pathlib.Path ):
    """
    Manages processing of mods-update.
    Called by: cli_start.py
    """
    ## get list of pids from file -----------------------------------
    pids: list = load_pids( pid_full_fpath )
    assert len( pids ) == 97
    ## load tracker -------------------------------------------------
    tracker = load_tracker( pid_full_fpath )
    ## loop over pids -----------------------------------------------
    for pid in pids:
        assert type(pid) == str
        ## check if pid has been processed --------------------------
        if check_if_pid_was_processed( pid, tracker ) == 'done':
            continue
        ## get mods -------------------------------------------------
        mods: str = get_mods( pid )
        ## update mods ----------------------------------------------
        updated_mods = update_mods( mods )
        ## save mods ------------------------------------------------
        save_mods( pid, updated_mods )
    pass


## helpers ----------------------------------------------------------


