# /usr/bin/python3

import os
import git
from datetime import datetime, timedelta
import json
import argparse
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

# Get file path
app_dir = os.path.dirname(__file__)

# Setup arg parse
desc = "This tool manages backs up and ArcGIS Online item to a local folder including definitions, data and features in the requested format"
parser = argparse.ArgumentParser(description=desc)
parser.add_argument("config", help="Config item defining items to backup", nargs="+")
parser.add_argument("-v", action="store_true", dest="verbose", help="Verbose, also logs debug messages")
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
logger = log.setup("backup_mgr", app_dir=app_dir, active=args.log)
# Update script log
tsstart = datetime.now()
tsstart_str = tsstart.strftime("%m/%d/%Y %H:%M:%S")
# Update status
log.post(logger, f"Script started at {tsstart_str}")
# Parse config files
for cfg in args.config:
    # Get config path
    cfg_path = os.path.abspath(cfg)
    logger.debug(f"Using config file at {cfg_path}")
    # Process config items
    with open(cfg_path, "r") as f:
        cfg = json.load(f)
    # Check if folder exists
    if not os.path.exists(cfg["outdir"]):
        # Build folder if not exists
        os.makedirs(cfg["outdir"])
    # Set as CWD
    os.chdir(cfg["outdir"])
    # Setup backup folder
    git_dir = os.path.join(cfg["outdir"], cfg["label"])
    # Setup git dir if not exists, else open
    if not os.path.exists(git_dir) or not os.path.exists(os.path.join(git_dir, ".git")):
        # Build folder if not exists
        repo = git.Repo.init(cfg["label"])
    else:
        repo = git.Repo(cfg["label"])
    # Write gitignore if absent
    if not os.path.exists('.gitignore'):
        # Write git ignore for ts files
        with open('.gitignore', 'w') as f:
            f.write('*.ts')
    # Get arcgis online connection object
    ago = agol.Agol(cfg["portal"], cfg["uname"], cfg["pword"], logger)
    # Check for error
    if ago:
        # Check if backing up admin or normal items
        if "admin" in cfg and cfg['admin']:
            # Update status
            log.post(logger, 'Collecting Admin Items')
            # Get options
            if 'options' in cfg['admin']:
                options = cfg['admin']["options"]
            else:
                options = 'all'
            # Get options
            if 'components' in cfg['admin']:
                components = cfg['admin']["components"]
            else:
                components = 'all'
            # Backup admin item
            backup_admin.run(ago.gis, git_dir, components, options, logger)
            # Update last backup time
            cfg['admin']["last"] = datetime.now().isoformat()
        try:
            # Update status
            log.post(logger, "Processing Items")
            # Process backup items
            for k, item in cfg["items"].items():
                # Get item id
                itemid = k
                log.post(logger, f" - {itemid}")
                # Check if backup is not yet due
                itmdir = os.path.join(git_dir, "items")
                #Check for due date
                if not os.path.exists(itmdir):
                    # If item folder does mark as due
                    item_due = True
                elif item["hours_diff"] > 0.0 and "last" in item:
                    # Setup diff with a 2% margin
                    diff = item["hours_diff"] * 0.98
                    # Check if item is due based on last run and hours_diff
                    last_run = datetime.fromisoformat(item['last'])
                    item_duedate = last_run + timedelta(hours=item["hours_diff"])
                    item_due = item_duedate < datetime.now()
                else:
                    item_due = True
                # Continue to next item if not due
                if not item_due:
                    log.post(logger, "  > Skipped, not yet due")
                    continue
                if item["hours_diff"] == 0.0:
                    log.post(logger, "  > Skipped, item set to ignore (hours_diff=0.0)")
                    continue
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
                # Run backup for item
                res = backup_item.run(ago.gis, itemid, git_dir, options, fmt, skip_unmodified=True, logger=logger)
                # Update status if appropriate
                if res.value > 1:
                    log.post(logger, f"  > Skipped, {res}")
                # Update last backup time
                item["last"] = datetime.now().isoformat()
                # Reset hours_diff if once requested
                if item["hours_diff"] == -1.0:
                    item["hours_diff"] == 0.0
            # Add all files and committ
            repo.git.add(all=True)
            repo.index.commit(f"Data commit @ {datetime.now()}")
        except Exception:
            # Report error and continue
            logger.exception('Unexpected error occured backing up files, please review code and try again.')
    # Setup last timestamp for config
    cfg["last"] = datetime.now().isoformat()
    # Update config items
    util.export_obj(cfg_path, cfg)
# Update log
tsend = datetime.now()
tsend_str = tsend.strftime("%m/%d/%Y %H:%M:%S")
sec = int((tsend - tsstart).total_seconds())
log.post(logger, f"Script finished at {tsend_str} after {sec} seconds")
