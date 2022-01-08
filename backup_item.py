# /usr/bin/python3

import os
from datetime import datetime
import logging
from arcgis.gis import GIS
import log
import util
import agol
import pathlib


def run(gis: GIS, itemid: str, directory: str, options: list, fmt: str, logger: logging):
    """Module to grab an item and its associated resources from ArcGIS Online and to save them to disk

    Args:
        gis (GIS): [description]
        itemid (str): ID of Arcgis Online item to backup
        directory (str): Output directory for data extracted in this tool
        options (list): Options for backup, currently supported options are item,data,metadata, thumbnail, url, sharing, appinfo, related, service or all
        fmt (str): Format for export of service (only works for the following types "Feature Service", "Vector Tile Service", "Scene Service")
        logger (logging): logging object to pass to tool for logging purposes
    """
    # Setup item folder
    directory = os.path.join(directory, "items")
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Get item
    item = gis.content.get(itemid)
    # Check if item exists
    if not item:
        # Update status
        logger.info("  > Item not found")
        # End module
        return
    # Clear our old and setup new dir
    item_dir = util.setup_dir(directory, itemid)
    # Backup status
    logger.debug("  Exporting:")
    # Check if requested
    if "item" in options or "all" in options:
        # Remove number of views as it changes each request and is always picked up in GIT change tracking
        del item["numViews"]
        # Update status
        logger.debug("  > Item")
        # Backup item
        util.export_agolclass(f"{item_dir}/content.json", item)
    # Check if requested
    if "data" in options or "all" in options:
        # Update status
        logger.debug("  > Data")
        # Backup meta
        datapath = item.download(item_dir, "data.json")
        # Move meta file
        if datapath:
            os.rename(datapath, datapath.replace(item["title"], "data"))
    # Check if requested
    if "metadata" in options or "all" in options:
        # Update status
        logger.debug("  > Metadata")
        # Backup meta, if it exists
        if "Metadata" in item["typeKeywords"]:
            item.download_metadata(item_dir)
    # Check if requested
    if "thumbnail" in options or "all" in options:
        # Update status
        logger.debug("  > Thumbnail")
        # Backup meta
        item.download_thumbnail(os.path.join(item_dir, "thumbnails"))
    # Check if requested
    if "url" in options or "all" in options:
        # Update status
        logger.debug("  > URL")
        # Backup url file
        util.export_url(f"{item_dir}/item.url", item.homepage)
    # Check if requested
    if "sharing" in options or "all" in options:
        # Update status
        logger.debug("  > Sharing")
        # Backup sharing
        util.export_obj(f"{item_dir}/sharing.json", item.shared_with)
    # Check if requested
    if "comments" in options or "all" in options:
        # Update status
        logger.debug("  > Comments")
        # Backup comments
        util.export_agolclass_list(f"{item_dir}/comments.json", item.comments)
    # Check if requested
    if "appinfo" in options or "all" in options:
        # Update status
        logger.debug("  > App Info")
        # Backup appinfo
        util.export_obj(f"{item_dir}/appinfo.json", item.app_info)
    # Check if requested
    if "related" in options or "all" in options:
        # Update status
        logger.debug("  > Related Items")
        # Backup related items
        related_items = {}
        reltypes = [
            "Map2Service",
            "WMA2Code",
            "Map2FeatureCollection",
            "MobileApp2Code",
            "Service2Data",
            "Service2Service",
            "Map2AppConfig",
            "Item2Attachment",
            "Item2Report",
            "Listed2Provisioned",
            "Style2Style",
            "Service2Style",
            "Survey2Service",
            "Survey2Data",
            "Service2Route",
            "Area2Package",
            "Map2Area",
            "Service2Layer",
            "Area2CustomPackage",
            "TrackView2Map",
            "SurveyAddIn2Data",
            "WorkforceMap2FeatureService",
            "Theme2Story",
            "WebStyle2DesktopStyle",
            "Solution2Item",
            "APIKey2Item",
        ]
        for r in reltypes:
            related_items[r] = {}
            related_items[r]["forward"] = item.related_items(r, "forward")
            related_items[r]["backward"] = item.related_items(r, "reverse")
        # Write related items to file
        util.export_obj(f"{item_dir}/related.json", related_items)
    # Check if requested
    if "service" in options or "all" in options:
        # Check type is compatible
        if item["type"] in ["Feature Service", "Vector Tile Service", "Scene Service"]:
            # Update Status
            logger.debug("  > Service")
            # Get requested fmt
            try:
                fmt = agol.EXPORT_FORMATS[fmt]
            except KeyError:
                fmt = agol.EXPORT_FORMATS["gdb"]
            # Setup title
            title = f"{item['name']}_tmpbackup"
            # Setup export
            export = item.export(title=title, export_fmt=fmt, wait=True, overwrite=True)
            # Grab data
            export.download(item_dir)
            # Delete export
            export.delete()


# Facilitate access to module standalone
if __name__ == "__main__":
    """Tool to faciliate access to associated module"""
    # Get file path
    app_dir = os.path.dirname(__file__)
    # Setup argparse if not called as a module
    import argparse
    desc = "This tool backs up and ArcGIS Online item to a local folder including its definition, data and features in the requested fmt"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("portal", help="AGOL portal")
    parser.add_argument("username", help="AGOL username")
    parser.add_argument("password", help="AGOL password")
    parser.add_argument("itemid", help="AGOL item id")
    parser.add_argument("outputdir", help="Output directory", type=pathlib.Path)
    parser.add_argument(
        "format",
        choices=agol.EXPORT_FORMATS.keys(),
        help="fmt to export features to (if features exist)",
    )
    parser.add_argument(
        "-o",
        "--options",
        dest="options",
        choices=[
            "item",
            "data",
            "metadata",
            "thumbnail",
            "url",
            "sharing",
            "appinfo",
            "related",
            "service",
            "all",
        ],
        default="all",
        help="Options for export",
        nargs="+",
    )
    parser.add_argument(
        "-v",
        action="store_true",
        dest="verbose",
        help="Verbose, also logs debug messages",
    )
    parser.add_argument(
        "-q",
        action="store_false",
        dest="log",
        help="Do not log script progress to file",
    )
    # Parse args
    args = parser.parse_args()
    # Setup logger
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = log.setup("backup_item", app_dir=app_dir, active=args.log, level=log_level)
    # Update script log
    tsstart = datetime.now()
    tsstart_str = tsstart.strftime("%m/%d/%Y %H:%M:%S")
    log.post(logger, f"Script started at {tsstart_str}")
    msg = f"Called with Args: {args.itemid} {args.outputdir} {args.format} {args.options}"
    logger.debug(msg)
    try:
        # Get arcgis online connection object
        ago = agol.Agol(args.portal, args.username, args.password, logger)
        # Check for errors
        if ago:
            # Update status
            log.post(logger, f" - Collecting Item {args.itemid}")
            # Run script with args
            run(ago.gis, itemid=args.itemid, directory=args.outputdir, fmt=args.format, options=args.options, logger=logger)
    except Exception:
        # Catch everything else
        log.post(logger, "Script failed unexpectedly", logging.ERROR)
        logger.exception()
    finally:
        # Update log
        tsend = datetime.now()
        tsend_str = tsend.strftime("%m/%d/%Y %H:%M:%S")
        sec = int((tsend - tsstart).total_seconds())
        log.post(logger, f"Script finished at {tsend_str} after {sec} seconds")
