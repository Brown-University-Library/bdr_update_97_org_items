import json, logging, os, pathlib

import httpx
from lxml import etree


log = logging.getLogger( __name__ )


## constants --------------------------------------------------------
MODS_URL_PATTERN = os.environ['U97__MODS_URL_PATTERN']


## helper functions -------------------------------------------------
## (manager function at bottom of file)


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


def create_tracker( pid_full_fpath: pathlib.Path ) -> pathlib.Path:
    """
    Creates tracker.
    Assumes tracker is in same directory as pid-file.
    Returns tracker filepath.
    """
    tracker_full_fpath = pid_full_fpath.parent.joinpath( 'tracker.json' )
    if tracker_full_fpath.exists():
        pass
    else:
        with open( tracker_full_fpath, 'w' ) as f:
            f.write( '{}' )
    return tracker_full_fpath


def create_record_info_element() -> etree.Element:  # type:ignore
    """
    Creates and returns a pre-built <mods:recordInfo> element, like this:
        <mods:recordInfo>
            <mods:recordInfoNote type="HallHoagOrgLevelRecord">Organization Record</mods:recordInfoNote>
        </mods:recordInfo>
    Builds this separately so it can be re-used for each MODS XML document.
    """
    record_info = etree.Element( '{http://www.loc.gov/mods/v3}recordInfo', attrib=None, nsmap=None )
    record_info_note = etree.SubElement(
        record_info,
        '{http://www.loc.gov/mods/v3}recordInfoNote',
        attrib={'type': 'HallHoagOrgLevelRecord'},
        nsmap=None
    )
    record_info_note.text = 'Organization Record'
    assert type(record_info) == etree._Element
    log.debug( f' type(record_info), ``{type(record_info)}``; record_info, ``{etree.tostring(record_info).decode("utf-8")}``' )
    return record_info


def check_if_pid_was_processed( pid: str, tracker_filepath: pathlib.Path ) -> str:
    """
    Check if pid was processed.
    """
    ## load tracker -------------------------------------------------
    with open( tracker_filepath, 'r' ) as f:
        tracker: dict = json.loads( f.read() )
        status = tracker.get( pid, 'not_done' )
    log.debug( f'pid, ``{pid}``; status, ``{status}``' )
    return status


def update_tracker( pid: str, tracker_filepath: pathlib.Path, status: str ) -> None:
    """
    Loads, updates, and re-saves tracker.
    """
    with open( tracker_filepath, 'w' ) as f:
        tracker: dict = json.loads( f.read() )
        tracker[ pid ] = status
        f.write( json.dumps( tracker, sort_keys=True, indent=2 ) )
    log.debug( f'updated-tracker for pid, ``{pid}`` with status, ``{status}``' )
    return


def get_mods( pid: str ) -> str:
    """
    Get mods using the constant.
    """
    mods_url: str = MODS_URL_PATTERN.format( PID=pid )
    log.debug( f'mods_url, ```{mods_url}```' )
    resp: httpx.Response = httpx.get( mods_url )
    mods: str = resp.content.decode( 'utf-8' )  # explicitly declare utf-8
    return mods


def check_if_element_exists( pid: str, mods: str, tracker_filepath: pathlib.Path ) -> bool:
    """
    Checks if element already exists.
    Returns boolean.
    If it does already exist, updates tracker.
    """
    if '<mods:recordInfo>' in mods:
        update_tracker( pid, tracker_filepath, 'already_exists' )
        return_val = True
    else:
        return_val = False
    log.debug( f'return_val, ``{return_val}``' )
    return return_val


def update_local_mods_string( original_mods_xml: str, PREBUILT_RECORD_INFO_ELEMENT: etree.Element ) -> str:  # type:ignore
    """
    Adds the pre-built <mods:recordInfo> element to the mods.
    Returns formatted XML string.
    """
    ## load initial string ------------------------------------------
    log.debug( f'original-mods, ``{original_mods_xml}``' )
    parser = etree.XMLParser( remove_blank_text=True )
    tree = etree.fromstring( original_mods_xml, parser=parser )
    ## add pre-built record-info element ----------------------------
    root: etree.Element = tree  # type:ignore
    root.append(etree.ElementTree(PREBUILT_RECORD_INFO_ELEMENT).getroot())
    ## convert back to string ---------------------------------------
    new_mods_xml = etree.tostring( 
        root, 
        pretty_print=True,                      # type:ignore
        xml_declaration=False,                  # type:ignore
        encoding='UTF-8' ).decode('utf-8')      # type:ignore
    log.debug( f'new-mods, ``{new_mods_xml}``' )
    return new_mods_xml


## manager function -------------------------------------------------


def manage_update( pid_full_fpath: pathlib.Path ) -> None:
    """
    Manages processing of mods-update.
    Called by: cli_start.py
    """
    ## get list of pids from file -----------------------------------
    pids: list = load_pids( pid_full_fpath )
    # assert len( pids ) == 97
    ## load tracker -------------------------------------------------
    tracker_filepath: pathlib.Path = create_tracker( pid_full_fpath )
    ## build the record-info element --------------------------------
    PREBUILT_RECORD_INFO_ELEMENT: etree.Element = create_record_info_element()  # type:ignore
    ## loop over pids -----------------------------------------------
    for pid in pids:
        assert type(pid) == str
        ## check if pid has been processed --------------------------
        if check_if_pid_was_processed( pid, tracker_filepath ) == 'done':
            continue
        ## get mods -------------------------------------------------
        mods: str = get_mods( pid )
        ## check if element already exists --------------------------
        if check_if_element_exists( pid, mods, tracker_filepath ) == True:
            continue
        ## update xml -----------------------------------------------
        updated_mods: str = update_local_mods_string( mods, PREBUILT_RECORD_INFO_ELEMENT )
        ## save back to BDR -----------------------------------------
        save_mods( pid, updated_mods )
    return


## helpers ----------------------------------------------------------


