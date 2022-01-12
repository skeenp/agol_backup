# /usr/bin/python3

import os
import shutil
import json
from datetime import datetime


def setup_dir(item_dir: str):
    """Removes existing dir and recreates a folder to hold new data, primarily used to facilitate change tracking

    Args:
        item_dir (str): Item directory to setup

    Returns:
        [str]: Path to directory setus in function
    """
    # Check if path exists
    if os.path.exists(item_dir):
        shutil.rmtree(item_dir)
    # Build item folder
    os.makedirs(item_dir)


def clean_dict(d: dict):
    """Cleans an Arcgis for Python API dict object by coping only dictionary items and removing system vars (i.e. those starting with '_')

    Args:
        d (dict): Dict to clean

    Returns:
        [dict]: Cleaned dict object
    """
    # Copy dict
    data = d.__dict__.copy()
    # Check if key starts with an underscore, if so ignore
    for k in list(data.keys()):
        # Check if key starts with an underscore, if so ignore
        if k.startswith("_"):
            del data[k]
    # Return cleaned dict
    return data


def clean_list(d: list):
    """Cleans an Arcgis for Python API list object by coping only dictionary items and removing system vars (i.e. those starting with '_')

    Args:
        d (list): List to clean

    Returns:
        [dict]: Cleaned dict object
    """
    # Process items in list
    data = []
    for itm in d:
        # Update to dict
        data.append(itm.__dict__.copy())
    for d in data:
        for k in list(d.keys()):
            # Remove sys variables
            if k.startswith("_"):
                del d[k]
            # Remove last login and numviews as it defaults essentially to now/last update + 1 and is always picked up in GIT change tracking
            if k in ['lastLogin', 'numViews']:
                del d[k]
    # Return cleaned list
    return data


def export_agolclass(out_path: str, data: object):
    """Export an Arcgis for Python API class object to path in json format

    Args:
        out_path (str): File path for export
        data (object): Data to export
    """
    # Open file object
    with open(out_path, "w") as f:
        # Clean dicts
        d = clean_dict(data)
        # Dump data
        json.dump(d, f, indent=2, sort_keys=True, default=str)


def export_agolclass_list(out_path: str, data: object):
    """Export an Arcgis for Python API class list object to path in json format

    Args:
        out_path (str):  File path for export
        data (object): Data to export
    """
    # Open file object
    with open(out_path, "w") as f:
        # Clean dicts
        d = clean_list(data)
        # Dump data
        json.dump(d, f, indent=2, sort_keys=True, default=str)


def export_obj(out_path: str, data: object):
    """Export object to path in json format

    Args:
        out_path (str): File path for export
        data (object): Data to export
    """
    # Open file object
    with open(out_path, "w") as f:
        # Dump data
        json.dump(data, f, indent=2, sort_keys=True, default=str)


def export_url(out_path: str, url: str):
    """Export url to a URL file

    Args:
        out_path (str): File path for export
        url (str): URL to export
    """
    # Open file object
    with open(out_path, "w") as f:
        # Dump data
        f.write(f"[InternetShortcut]\nURL={url}")


def get_ts(file: str):
    """Gets standardised timestamp file

    Args:
        file (str): source timestamp file
    """
    # Get last change date
    try:
        # Load timestamp file
        with open(file, 'r') as f:
            ts = datetime.fromisoformat(json.load(f))
    except IOError:
        # Default to the start of time if timestamp file does not exist
        ts = datetime.min
    return ts


def set_ts(file: str):
    """Sets standardised timestamp file

    Args:
        file (str): destination timestamp file
    """
    # Write out timestamp file
    export_obj(file, datetime.now().isoformat())
