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

"""Script to leverage the functionality of backup_admin and backup_item to manage a series of backups for an AGOL account"""

# Run cert override
os.environ['REQUESTS_CA_BUNDLE'] = "certifi/cacert.pem"

# Get file path
app_dir = os.path.dirname(__file__)

# Setup arg parse
desc = "This tool manages backs up and ArcGIS Online item to a local folder including definitions, data and features in the requested format"
parser = argparse.ArgumentParser(description=desc)
parser.add_argument("config", help="Config item defining items to backup")
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
logger = log.setup("backup_manager", app_dir=app_dir, active=args.log)
# Update script log
tsstart = datetime.now()
tsstart_str = tsstart.strftime("%m/%d/%Y %H:%M:%S")
# Update status
log.post(logger, f"Script started at {tsstart_str}")
# Get config path
cfg_path = os.path.abspath(args.config)
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
# Get arcgis online connection object
ago = agol.Agol(cfg["portal"], cfg["uname"], cfg["pword"], logger)
# Check for error
if ago:
    # Update status
    log.post(logger, "Processing Items")
    # Process backup items
    for item in cfg["items"]:
        # Get item id
        itemid = item["itemid"]
        log.post(logger, f" - {itemid}")
        # Check if backup is not yet due
        if "last" in item:
            last_run = datetime.fromisoformat(item['last'])
            item_duedate = last_run + timedelta(hours=item["hours_diff"])
            item_due = item_duedate < datetime.now()
        else:
            item_due = True
        # Continue to next item if not due
        if not item_due:
            log.post(logger, "  > Skipped, not yet due")
            continue
        # Check if backing up admin or normal items
        if itemid == "admin":
            # Get options
            if 'options' in item:
                options = item["options"]
            else:
                options = 'all'
            # Get options
            if 'components' in item:
                components = item["components"]
            else:
                components = 'all'
            # Backup admin item
            backup_admin.run(ago.gis, git_dir, components, options, logger)
            # Update last backup time
            item["last"] = datetime.now().isoformat()
        else:
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
            backup_item.run(ago.gis, item["itemid"], git_dir, options, fmt, logger)
            # Update last backup time
            item["last"] = datetime.now().isoformat()
    # Add all files and committ
    repo.git.add(all=True)
    repo.index.commit(f"Data commit @ {datetime.now()}")
# Setup last timestamp for config
cfg["last"] = datetime.now().isoformat()
# Update config items
util.export_obj(cfg_path, cfg)
# Update log
tsend = datetime.now()
tsend_str = tsend.strftime("%m/%d/%Y %H:%M:%S")
sec = int((tsend - tsstart).total_seconds())
log.post(logger, f"Script finished at {tsend_str} after {sec} seconds")
