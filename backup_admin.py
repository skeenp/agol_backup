import os
from datetime import datetime
import logging
from arcgis.gis import GIS
import log
import util
import agol
import pathlib


def run(gis: GIS, directory: str, components: list, options: list, logger: logging):
    """Module to grab admin items and their associated resources from ArcGIS Online and to save them to disk

    Args:
        gis (GIS): arcgis.gis.GIS object from the Arcgis for Python API
        directory (str): Output directory for data extracted in this tool
        components (list): Components to backup, currently supported components are users, groups, me or all.
        options (list): Options for backup, currently supported options are item, groups, usrtypes, folders, linked, items, url, thumbnail, members and all
        logger (logging): logging object to pass to tool for logging purposes
    """
    # Setup groups folder
    directory = os.path.join(directory, "admin")
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Update status
    logger.debug("  Exporting:")
    # Determine if groups are to exported
    if "groups" in components or "all" in components:
        # Update status
        logger.debug("  > Groups")
        # Setup groups folder
        group_dir = os.path.join(directory, "groups")
        if not os.path.exists(group_dir):
            os.makedirs(group_dir)
        # Process groups
        for group in gis.groups.search():
            # Setup group dir path
            grp_dir = util.setup_dir(group_dir, group["id"])
            # Get group if requested
            if "item" in options or "all" in options:
                # Update status
                logger.debug("  > Group Info")
                grp_path = f"{grp_dir}/group.json"
                util.export_agolclass(grp_path, group)
            # Get group members if requested
            if "members" in options or "all" in options:
                # Update status
                logger.debug("  > Members")
                grp_members = f"{grp_dir}/members.json"
                util.export_obj(grp_members, group.get_members())
            # Get content if requested
            if "items" in options or "all" in options:
                # Update status
                logger.debug("  > Items")
                grp_items = f"{grp_dir}/items.json"
                util.export_agolclass_list(grp_items, group.content(9999))
            # Get URL if requested
            if "url" in options or "all" in options:
                # Update status
                logger.debug("  > URL")
                util.export_url(f"{grp_dir}/group.url", group.homepage)
            # Get thumbnail if requested
            if "thumbnail" in options or "all" in options:
                # Update status
                logger.debug("  > Thumbnail")
                group.download_thumbnail(grp_dir)
    # Determine if users are to exported
    if "users" in components or "all" in components:
        # Update status
        logger.debug("  > Users")
        # Setup groups folder
        users_dir = os.path.join(directory, "users")
        if not os.path.exists(users_dir):
            os.makedirs(users_dir)
        # Process groups
        for user in gis.users.search():
            # Setup group dir path
            usr_dir = util.setup_dir(users_dir, user["id"])
            # Update user groups if requested
            if "item" in options or "all" in options:
                # Update status
                logger.debug("  > User Info")
                usr_path = f"{usr_dir}/user.json"
                util.export_agolclass(usr_path, user)
            # Save URL if requested
            if "url" in options or "all" in options:
                # Update status
                logger.debug("  > URL")
                usr_url = f"{usr_dir}/user.url"
                util.export_url(usr_url, user.homepage)
            # Get thumbnail if requested
            if "thumbnail" in options or "all" in options:
                # Update status
                logger.debug("  > Thumbnail")
                user.download_thumbnail(usr_dir)
    # Determine if self are to exported
    if "me" in components or "all" in components:
        # Update status
        logger.debug("  > Me")
        # Setup groups folder
        me_dir = os.path.join(directory, "me")
        if not os.path.exists(me_dir):
            os.makedirs(me_dir)
        # Process user
        user = gis.users.me
        # Remove last login as it defaults essentially to now and is always picked up in GIT change tracking
        del user["lastLogin"]
        # Setup group dir path
        usr_dir = util.setup_dir(me_dir, user["id"])
        # Update user if requested
        if "item" in options or "all" in options:
            # Update status
            logger.debug("  > User Info")
            usr_path = f"{usr_dir}/user.json"
            util.export_agolclass(usr_path, user)
        # Get groups if requested
        if "groups" in options or "all" in options:
            # Update status
            logger.debug("  > Groups")
            usr_grps = f"{usr_dir}/groups.json"
            util.export_agolclass_list(usr_grps, user.groups)
        # Get user types if requested
        if "usrtypes" in options or "all" in options:
            # Update status
            logger.debug("  > User Types")
            usrtyp_path = f"{usr_dir}/usertypes.json"
            util.export_agolclass(usrtyp_path, user.user_types)
        # Get folders if requested
        if "folders" in options or "all" in options:
            # Update status
            logger.debug("  > Folders")
            usr_folders = f"{usr_dir}/folders.json"
            util.export_obj(usr_folders, user.folders)
        # Get linked accounts if requested
        if "linked" in options or "all" in options:
            # Update status
            logger.debug("  > Linked Accounts")
            usr_linkedacc = f"{usr_dir}/linked_accounts.json"
            util.export_agolclass_list(usr_linkedacc, user.linked_accounts)
        # Get content if requested
        if "items" in options or "all" in options:
            # Update status
            logger.debug("  > Items")
            usr_cnt = f"{usr_dir}/items.json"
            util.export_agolclass_list(usr_cnt, user.items(max_items=9999))
        # Save URL if requested
        if "url" in options or "all" in options:
            # Update status
            logger.debug("  > URL")
            usr_url = f"{usr_dir}/me.url"
            util.export_url(usr_url, user.homepage)
        # Get thumbnail if requested
        if "thumbnail" in options or "all" in options:
            # Update status
            logger.debug("  > Thumbnail")
            user.download_thumbnail(usr_dir)


if __name__ == "__main__":
    """Tool to faciliate access to associated module"""
    # Get file path
    app_dir = os.path.dirname(__file__)
    # Setup argparse if not called as a module
    import argparse
    desc = "This tool backs up and ArcGIS Online admin item to a JSON file"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("portal", help="AGOL Portal")
    parser.add_argument("username", help="AGOL Username")
    parser.add_argument("password", help="AGOL Password")
    parser.add_argument("outputdir", help="Output directory", type=pathlib.Path)
    parser.add_argument(
        "-c",
        "--components",
        dest="components",
        choices=["groups", "users", "me", "all"],
        default="all",
        help="Types to export",
        nargs="+",
    )
    parser.add_argument(
        "-o",
        "--options",
        dest="options",
        choices=[
            "item",
            "groups",
            "usrtypes",
            "folders",
            "linked",
            "items", "url",
            "thumbnail",
            "members",
            "all",
        ],
        default="all",
        help="Types to export",
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
    logger = log.setup("backup_admin", active=args.log, app_dir=app_dir, level=log_level)
    # Update script log
    tsstart = datetime.now()
    tsstart_str = tsstart.strftime("%m/%d/%Y %H:%M:%S")
    log.post(logger, f"Script started at {tsstart_str}")
    msg = f"Called with Args: {args.itemid} {args.outputdir} {args.format} {args.components} {args.options}"
    logger.debug(msg)
    try:
        # Get arcgis online connection object
        ago = agol.Agol(args.portal, args.username, args.password, logger)
        # Update status
        log.post(logger, " - Collecting Admin Items")
        # Run with args
        run(ago.gis, args.outputdir, args.components, args.options, logger)
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
