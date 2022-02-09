import os
from datetime import datetime
import logging
from arcgis.gis import GIS
import log
import util
import agol
import pathlib

_options = {'self': ['item', 'groups', 'usrtypes', 'folders', 'linked', 'items', 'url', 'thumbnail', 'all'],
            'users': ['item', 'url', 'thumbnail', 'all'],
            'groups': ['item', 'items', 'url', 'thumbnail', 'members', 'all']}


def backup_self(gis: GIS, directory: str, options: list, logger: logging):
    """Module to grab self items and their associated resources from ArcGIS Online and to save them to disk

    Args:
        gis (GIS): arcgis.gis.GIS object from the Arcgis for Python API
        directory (str): Output directory for data extracted in this tool
        options (list): Options for backup, currently supported options are item, groups, usrtypes, folders, linked, items, url, thumbnail and all
        logger (logging): logging object to pass to tool for logging purposes
    """
    # Setup admin folder
    directory = os.path.join(directory, "admin")
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Process user
    user = gis.users.me
    # Setup user path
    usr_dir = os.path.join(directory, user["id"])
    # Setup group dir path
    util.setup_dir(usr_dir)
    # Update user if requested
    if "item" in options or "all" in options:
        # Update status
        logger.debug(" > User Info")
        usr_path = f"{usr_dir}/user.json"
        # Export data
        util.export_agolclass(usr_path, user)
    # Get groups if requested
    if "groups" in options or "all" in options:
        # Update status
        logger.debug(" > Groups")
        usr_grps = f"{usr_dir}/groups.json"
        util.export_agolclass_list(usr_grps, user.groups)
    # Get user types if requested
    if "usrtypes" in options or "all" in options:
        # Update status
        logger.debug(" > User Types")
        usrtyp_path = f"{usr_dir}/usertypes.json"
        util.export_agolclass(usrtyp_path, user.user_types)
    # Get folders if requested
    if "folders" in options or "all" in options:
        # Update status
        logger.debug(" > Folders")
        usr_folders = f"{usr_dir}/folders.json"
        util.export_obj(usr_folders, user.folders)
    # Get linked accounts if requested
    if "linked" in options or "all" in options:
        # Update status
        logger.debug(" > Linked Accounts")
        usr_linkedacc = f"{usr_dir}/linked_accounts.json"
        util.export_agolclass_list(usr_linkedacc, user.linked_accounts)
    # Get content if requested
    if "items" in options or "all" in options:
        # Update status
        logger.debug(" > Items")
        usr_cnt = f"{usr_dir}/items.json"
        # Setup items var
        items = []
        # Preporocess items
        for i in user.items(max_items=9999):
            # Get item dict
            items.append(i)
        util.export_agolclass_list(usr_cnt, items)
    # Save URL if requested
    if "url" in options or "all" in options:
        # Update status
        logger.debug(" > URL")
        usr_url = f"{usr_dir}/me.url"
        util.export_url(usr_url, user.homepage)
    # Get thumbnail if requested
    if "thumbnail" in options or "all" in options:
        # Update status
        logger.debug(" > Thumbnail")
        user.download_thumbnail(usr_dir)
    # Write timestamp
    util.set_ts(os.path.join(directory, 'lastupdate.ts'))


def backup_users(gis: GIS, directory: str, options: list, logger: logging):
    """Module to grab user items and their associated resources from ArcGIS Online and to save them to disk

    Args:
        gis (GIS): arcgis.gis.GIS object from the Arcgis for Python API
        directory (str): Output directory for data extracted in this tool
        options (list): Options for backup, currently supported options are item, url, thumbnail and all
        logger (logging): logging object to pass to tool for logging purposes
    """
    # Setup groups folder
    directory = os.path.join(directory, "admin")
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Setup groups folder
    users_dir = os.path.join(directory, "users")
    if not os.path.exists(users_dir):
        os.makedirs(users_dir)
    # Process groups
    for user in gis.users.search():
        # Setup user path
        usr_dir = os.path.join(users_dir, user["id"])
        # Setup group dir path
        util.setup_dir(usr_dir)
        # Update user groups if requested
        if "item" in options or "all" in options:
            # Update status
            logger.debug(" > User Info")
            usr_path = f"{usr_dir}/user.json"
            # Export data
            util.export_agolclass(usr_path, user)
        # Save URL if requested
        if "url" in options or "all" in options:
            # Update status
            logger.debug(" > URL")
            usr_url = f"{usr_dir}/user.url"
            util.export_url(usr_url, user.homepage)
        # Get thumbnail if requested
        if "thumbnail" in options or "all" in options:
            # Update status
            logger.debug(" > Thumbnail")
            user.download_thumbnail(usr_dir)
    # Write timestamp
    util.set_ts(os.path.join(directory, 'lastupdate.ts'))


def backup_groups(gis: GIS, directory: str, options: list, logger: logging):
    """Module to grab group items and their associated resources from ArcGIS Online and to save them to disk

    Args:
        gis (GIS): arcgis.gis.GIS object from the Arcgis for Python API
        directory (str): Output directory for data extracted in this tool
        options (list): Options for backup, currently supported options are item, items, url, thumbnail, members and all
        logger (logging): logging object to pass to tool for logging purposes
    """
    # Setup groups folder
    directory = os.path.join(directory, "admin")
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Setup groups folder
    group_dir = os.path.join(directory, "groups")
    if not os.path.exists(group_dir):
        os.makedirs(group_dir)
    # Process groups
    for group in gis.groups.search():
        # Setup group path
        grp_dir = os.path.join(group_dir, group["id"])
        # Setup group dir path
        util.setup_dir(grp_dir)
        # Get group if requested
        if "item" in options or "all" in options:
            # Update status
            logger.debug(" > Group Info")
            grp_path = f"{grp_dir}/group.json"
            util.export_agolclass(grp_path, group)
        # Get group members if requested
        if "members" in options or "all" in options:
            # Update status
            logger.debug(" > Members")
            grp_members = f"{grp_dir}/members.json"
            util.export_obj(grp_members, group.get_members())
        # Get content if requested
        if "items" in options or "all" in options:
            # Update status
            logger.debug(" > Items")
            grp_items = f"{grp_dir}/items.json"
            # Setup items var
            items = []
            # Preporocess items
            for i in group.content(9999):
                # Add item to list
                items.append(i)
            util.export_agolclass_list(grp_items, items)
        # Get URL if requested
        if "url" in options or "all" in options:
            # Update status
            logger.debug(" > URL")
            util.export_url(f"{grp_dir}/group.url", group.homepage)
        # Get thumbnail if requested
        if "thumbnail" in options or "all" in options:
            # Update status
            logger.debug(" > Thumbnail")
            group.download_thumbnail(grp_dir)
    # Write timestamp
    util.set_ts(os.path.join(directory, 'lastupdate.ts'))


if __name__ == "__main__":
    """Tool to faciliate access to associated module"""
    # Get file path
    app_dir = os.path.dirname(__file__)
    # Setup argparse if not called as a module
    import argparse
    desc = "This tool backs up an ArcGIS Online group item to a JSON file"
    parser = argparse.ArgumentParser(description=desc)
    #Setup parent parser
    component_parser = argparse.ArgumentParser(add_help=False)
    component_parser.required = True
    component_parser.add_argument("portal", help="AGOL Portal")
    component_parser.add_argument("username", help="AGOL Username")
    component_parser.add_argument("password", help="AGOL Password")
    component_parser.add_argument("outputdir", help="Output directory", type=pathlib.Path)
    component_parser.add_argument(
        "-v",
        action="store_true",
        dest="verbose",
        help="Verbose, also logs debug messages",
    )
    component_parser.add_argument(
        "-q",
        action="store_false",
        dest="nolog",
        help="Do not log script progress to file",
    )
    # Build subparsers
    subparsers = parser.add_subparsers(title='components', dest='component', help="component to export")
    subparsers.required = True
    self_parser = subparsers.add_parser('self', parents=[component_parser])
    user_parser = subparsers.add_parser('user', parents=[component_parser])
    group_parser = subparsers.add_parser('group', parents=[component_parser])
    #Setup options for parsers
    self_parser.add_argument(
        "-o",
        dest="options",
        choices=_options['self'],
        default="all",
        help="Options for export",
        nargs="+",
    )
    user_parser.add_argument(
        "-o",
        dest="options",
        choices=_options['users'],
        default="all",
        help="Options for export",
        nargs="+"
    )
    group_parser.add_argument(
        "-o",
        dest="options",
        choices=_options['groups'],
        default="all",
        help="Options for export",
        nargs="+",
    )
    # Parse args
    args = parser.parse_args()
    # Setup logger
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = log.setup("backup_admin", active=args.nolog, app_dir=app_dir, level=log_level)
    # Update script log
    tsstart = datetime.now()
    tsstart_str = tsstart.strftime("%m/%d/%Y %H:%M:%S")
    log.post(logger, f"Script started at {tsstart_str}")
    msg = f"Called with Args: {args.component} {args.portal} {args.outputdir} {args.options}"
    logger.debug(msg)
    try:
        # Get arcgis online connection object
        ago = agol.Agol(args.portal, args.username, args.password, logger)
        # Update status
        log.post(logger, "- Collecting Group Items")
        # Run with args
        if args.component == 'self':
            backup_self(ago.gis, directory=args.outputdir, options=args.options, logger=logger)
        elif args.component == 'users':
            backup_users(ago.gis, directory=args.outputdir, options=args.options, logger=logger)
        elif args.component == 'self':
            backup_groups(ago.gis, directory=args.outputdir, options=args.options, logger=logger)
            
    except Exception:
        # Catch everything else
        msg = "Script failed unexpectedly"
        log.post(logger, msg, logging.ERROR)
        logger.exception(msg)
    finally:
        # Update log
        tsend = datetime.now()
        tsend_str = tsend.strftime("%m/%d/%Y %H:%M:%S")
        sec = int((tsend - tsstart).total_seconds())
        log.post(logger, f"Script finished at {tsend_str} after {sec} seconds")
