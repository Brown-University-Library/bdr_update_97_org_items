import json, logging, pathlib

import httpx
from lxml import etree


log = logging.getLogger( __name__ )


## constants --------------------------------------------------------
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


def create_record_info_element() -> etree.Element:
    """
    Creates and returns a pre-built <mods:recordInfo> element, like this:
        <mods:recordInfo>
            <mods:recordInfoNote type="HallHoagOrgLevelRecord">Organization Record</mods:recordInfoNote>
        </mods:recordInfo>
    Builds this separately so it can be re-used for each MODS XML document.
    """
    record_info = etree.Element('{http://www.loc.gov/mods/v3}recordInfo')
    record_info_note = etree.SubElement(
        record_info,
        '{http://www.loc.gov/mods/v3}recordInfoNote',
        attrib={'type': 'HallHoagOrgLevelRecord'}
    )
    record_info_note.text = 'Organization Record'
    return record_info


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


def update_local_mods_string( original_mods_xml: str, PREBUILT_RECORD_INFO_ELEMENT: etree.Element ) -> str:
    """
    Adds the pre-built <mods:recordInfo> element to the mods.
    Returns formatted XML string.
    """
    ## load initial string ------------------------------------------
    parser = etree.XMLParser( remove_blank_text=True )
    tree = etree.fromstring(original_mods_xml, parser=parser)
    ## add pre-built record-info element ----------------------------
    root: etree.Element = tree
    root.append(etree.ElementTree(PREBUILT_RECORD_INFO_ELEMENT).getroot())
    ## convert back to string ---------------------------------------
    new_mods_xml = etree.tostring( 
        root, 
        pretty_print=True, 
        xml_declaration=False, 
        encoding='UTF-8' ).decode('utf-8')
    return new_mods_xml


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
    ## build the record-info element --------------------------------
    PREBUILT_RECORD_INFO_ELEMENT: etree.Element = create_record_info_element()
    ## loop over pids -----------------------------------------------
    for pid in pids:
        assert type(pid) == str
        ## check if pid has been processed --------------------------
        if check_if_pid_was_processed( pid, tracker ) == 'done':
            continue
        ## get mods -------------------------------------------------
        mods: str = get_mods( pid )
        ## update xml -----------------------------------------------
        log.debug( f'initial-mods, ``{mods}``' )
        updated_mods: str = update_local_mods_string( mods, PREBUILT_RECORD_INFO_ELEMENT )
        log.debug( f'updated-mods, ``{updated_mods}``' )
        ## save back to BDR -----------------------------------------
        save_mods( pid, updated_mods )
    pass


## helpers ----------------------------------------------------------


