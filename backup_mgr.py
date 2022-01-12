# /usr/bin/python3

import os
import git
from datetime import datetime, timedelta
import json
import logging
import log
import util
import agol
import backup_admin
import backup_item

# TODO: Multithreading on item download

"""Script to leverage the functionality of backup_admin and backup_item to manage a series of backups for an AGOL account"""

# Run cert override
os.environ['REQUESTS_CA_BUNDLE'] = "certifi/cacert.pem"


def run(cfg_paths: list, logger: logging, reset: bool = False):
    """Module to manage backups as defined in a backup config file

    Args:
        cfg_paths (str): List of paths to config files to process
        logger (logging): logging object to pass to tool for logging purposes
        reset (bool): Ignores timestamps and resets download timing logic (Default false)
    """
    # Parse config files
    for cfg in cfg_paths:
        # Get config path
        cfg_path = os.path.abspath(cfg)
        log.post(logger, f"Using config file at {cfg_path}")
        # Check config file exists
        if not os.path.exists(cfg_path):
            log.post(logger, " - Config file not found")
        # Process config items
        with open(cfg_path, "r") as f:
            cfg = json.load(f)
        # Check if folder exists
        if not os.path.exists(cfg["outdir"]):
            # Build folder if not exists
            os.makedirs(cfg["outdir"])
        # Setup backup folder
        backup_dir = os.path.join(cfg["outdir"], cfg["label"])
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        # Default git var
        usegit = cfg['usegit'] if 'usegit' in cfg else True
        # Setup git if requested
        if usegit:
            # Setup git dir if not exists, else open
            if not os.path.exists(os.path.join(backup_dir, ".git")):
                # Build folder if not exists
                repo = git.Repo.init(backup_dir)
            else:
                repo = git.Repo(backup_dir)
            # Write gitignore if absent
            gitignore_path = os.path.join(backup_dir, '.gitignore')
            if not os.path.exists(gitignore_path):
                # Write git ignore for ts files
                with open(gitignore_path, 'w') as f:
                    f.write('*.ts')
        # Get arcgis online connection object
        ago = agol.Agol(cfg["portal"], cfg["uname"], cfg["pword"], logger)
        # Check for error
        if ago:
            # Check if backing up admin or normal items
            if "admin" in cfg and cfg['admin']:
                # Update status
                log.post(logger, 'Collecting Admin Items')
                # Setup admin var
                admin = cfg['admin']
                # Get options
                if 'options' in admin:
                    options = admin["options"]
                else:
                    options = 'all'
                # Get options
                if 'components' in admin:
                    components = admin["components"]
                else:
                    components = 'all'
                # Check for due date
                if reset:
                    admin_due = True
                elif not os.path.exists(backup_dir):
                    # If item folder does mark as due
                    admin_due = True
                elif admin["hours_diff"] == 0.0:
                    # If item is set at 0, skip
                    log.post(logger, " > Skipped admin, item set to ignore (hours_diff=0.0)")
                    admin_due = False
                elif admin["hours_diff"] > 0.0:
                    # Setup diff with a 2% margin
                    diff = admin * 0.98
                    # Get last run date
                    last_run = datetime.fromisoformat(admin["last"]) if 'last' in admin else 0
                    # Check if item is due based on last run and hours_diff
                    admin_duedate = last_run + timedelta(hours=diff)
                    admin_due = admin_duedate < datetime.now()
                else:
                    # Default to due
                    admin_due = True
                # Check if due
                if admin_due:
                    # Backup admin item
                    backup_admin.run(ago.gis, backup_dir, components, options, logger)
                    log.post(logger, " > Admin successfully backed up")
                else:
                    # Update status
                    log.post(logger, " > Skipped admin, not due yet")
            # Process items
            try:
                # Update status
                log.post(logger, "Processing Items")
                # Process backup items
                for k, item in cfg["items"].items():
                    # Get item id
                    itemid = k
                    log.post(logger, f" - {itemid}")
                    # Check if backup is not yet due
                    itmdir = os.path.join(backup_dir, "items")
                    # Get format
                    if "format" in item:
                        fmt = item["format"]
                    else:
                        fmt = None
                    # Get options
                    if 'options' in item:
                        options = item["options"]
                    else:
                        options = 'all'
                    # Check for due date
                    if reset:
                        admin_due = True
                    elif not os.path.exists(itmdir):
                        # If item folder does mark as due
                        item_due = True
                    elif item["hours_diff"] == 0.0:
                        # If item is set at 0, skip
                        log.post(logger, " > Skipped item, item set to ignore (hours_diff=0.0)")
                        admin_due = False
                    elif item["hours_diff"] > 0.0:
                        # Setup diff with a 2% margin
                        diff = item["hours_diff"] * 0.98
                        # Check if item is due based on last run and hours_diff
                        last_run = util.get_ts(os.path.join(itmdir, itemid, 'lastupdate.ts'))
                        item_duedate = last_run + timedelta(hours=diff)
                        item_due = item_duedate < datetime.now()
                    else:
                        item_due = True
                    # Continue to next item if not due
                    if item_due:
                        # Run backup for item
                        skipunmod = False if reset else True
                        res = backup_item.run(ago.gis, itemid, backup_dir, options, fmt, skip_unmodified=skipunmod, logger=logger)
                        # Update status if appropriate
                        if res.value > 1:
                            log.post(logger, f" > Skipped item, {res}")
                    else:
                        log.post(logger, " > Skipped item, not yet due")
            except Exception:
                # Report error and continue
                logger.exception('Unexpected error occured backing up files, please review code and try again.')
        # Commit changes to git repo
        if usegit:
            # Add all files and committ
            repo.git.add(all=True)
            repo.index.commit(f"Data commit @ {datetime.now()}")


if __name__ == '__main__':
    # Get file path
    app_dir = os.path.dirname(__file__)
    # Setup arg parse
    import argparse
    # Setup arg parse
    desc = "This tool manages backs up and ArcGIS Online item to a local folder including definitions, data and features in the requested format"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-c', '--config', dest='config', help="Config item defining items to backup", nargs='+')
    parser.add_argument("-v", action="store_true", dest="verbose", help="Verbose, also logs debug messages")
    parser.add_argument(
        "-r",
        action="store_true",
        dest="reset",
        help="Reset items by ignoring timestamps",
    )
    parser.add_argument(
        "-q",
        action="store_false",
        dest="nolog",
        help="Do not log script progress to file",
    )
    # Parse args
    args = parser.parse_args()
    # Setup logger
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = log.setup("backup_mgr", app_dir=app_dir, active=args.nolog, level=log_level)
    # Update script log
    tsstart = datetime.now()
    tsstart_str = tsstart.strftime("%m/%d/%Y %H:%M:%S")
    # Update status
    log.post(logger, f"Script started at {tsstart_str}")
    # Run script
    msg = f"Called with Args: {args.config}"
    logger.debug(msg)
    try:
        # Run script with args
        run(cfg_paths=args.config, logger=logger, reset=args.reset)
    except Exception:
        # Catch everything else
        log.post(logger, "Script failed unexpectedly", logging.ERROR)
        logger.exception('Script Failed')
    finally:
        # Update log
        tsend = datetime.now()
        tsend_str = tsend.strftime("%m/%d/%Y %H:%M:%S")
        sec = int((tsend - tsstart).total_seconds())
        log.post(logger, f"Script finished at {tsend_str} after {sec} seconds")
