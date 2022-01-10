# ArcGIS Online Backup Utility V01

This project provides scripts and a windows exe which allows you to easily manage and schedule backups to your content on ArcGIS Online. 

## Getting Started

These instructions will give you a copy of the project to get it up and running on your local machine for development and testing purposes. See deployment for notes on deploying the project on a live system.

### Prerequisites

Requirements for the software and other tools to build, test and push 
- [Python 3](https://www.python.org/)
- [ArcGIS Online or Portal Account](https://www.arcgis.com/)

### Installing

A step by step series of examples that tell you how to get a development environment running. It is recomended to setup a virtual environment for running this project, especially if you plan to build it to and exe or equilivant file.

#### Setup Virtual Environment

``` Python
# Setup environment
python -m venv venv
# Activate environment
venv\Scripts\activate.bat
``` 

#### [Optional] Install ArcGIS API for Python with no dependancies.
This step can be handled by the requirements.txt file, however it will install the full ArcGIS API for Python which contains much more than is needed for this app. It is being managed manually here to reduce the size of files compiled for the window executable.

```
pip install arcgis --no-deps
```

#### Install requirements

```Cmd
# Upgrade
python -m pip install --upgrade pip 
#Install requirements
pip install -r requirements.txt
```

## Use

This project is provided in two forms, as a windows executable and as a series of python scripts. The executables are just a packaged version of the python scripts.

### Setup & Scheduling

To setup an environment for scheduled backups, first build a config file using backup_cfg_mgr (see below). Once setup, setup a schedule in your operating system to run the scripts according to a schedule. The schedule should be no longer than your shortest hour delay period. For example, if one of your backups are requested hourly, run your script hourly. Multiple config files can be specified and passed to backup_mgr

### Accessing Backups

Backups are committed to a local git repo. Using your preferred git client i.e. [Github Desktop](https://desktop.github.com/), you can access previous versions and updates to data. The script does not manage git folder size, so you will want to keep an eye on the size of your repo and perhaps clean it up periodically to flush old backups.

### Python Scripts

There are three python scripts available in the project.

#### backup_mgr.py
This tool manages backs up and ArcGIS Online item to a local folder including definitions, data and features in the requested format
```
positional arguments:
  config      Config item(s) defining items to backup (see sample config folder)

optional arguments:
  -h, --help  show this help message and exit
  -v          Verbose, also logs debug messages
  -q          Do not log script progress to file
```

#### backup_item.py
This tool backs up and ArcGIS Online item to a local folder including its definition, data and features in the requested fmt
```
positional arguments:
  portal                AGOL portal
  username              AGOL username
  password              AGOL password
  itemid                AGOL item id
  outputdir             Output directory
  {csv,shp,geojson,fgdb,gpkg,kml,spkg,vtpk,xls,none}
                        fmt to export features to (if features exist)

optional arguments:
  -h, --help            show this help message and exit
  -o {item,data,metadata,thumbnail,url,sharing,appinfo,related,service,all} [{item,data,metadata,thumbnail,url,sharing,appinfo,related,service,all} ...], --options {item,data,metadata,thumbnail,url,sharing,appinfo,related,service,all} [{item,data,metadata,thumbnail,url,sharing,appinfo,related,service,all} ...]
                        Options for export
  -s                    Skip modified items (works when backing up to the same location as last time)
  -v                    Verbose, also logs debug messages
  -q                    Do not log script progress to file
```

#### backup_admin.py

This tool backs up and ArcGIS Online admin item to a JSON file

```
positional arguments:
  portal                AGOL Portal
  username              AGOL Username
  password              AGOL Password
  outputdir             Output directory

optional arguments:
  -h, --help            show this help message and exit
  -c, --components {groups,users,me,all} [{groups,users,me,all} ...]
                        Types to export
  -o,--options  {item,groups,usrtypes,folders,linked,items,url,thumbnail,members,all} [{item,groups,usrtypes,folders,linked,items,url,thumbnail,members,all} ...],
                        Types to export
  -v                    Verbose, also logs debug messages
  -q                    Do not log script progress to file
```

#### backup_cfg_mgr.py

This manages config files for backup_mgr

```
positional arguments:
  config      Config item defining items to backup (see sample config folder)

optional arguments:
  -h, --help  show this help message and exit
  -v          Verbose, also logs debug messages
  -q          Do not log script progress to file
```

### Executable

The execuatables mirror the definition of scripts above.


## Building Standalong App

To build a standalone version of the app, compile with pyinstaller
``` CMD
# Backup Manager
pyinstaller --noconfirm --onefile --console --icon "img/backup_gui.ico" --add-data "certifi;certifi"  "backup_mgr.py"

#Backup Item (Optional)
pyinstaller --noconfirm --onefile --console --icon "img/backup_gui.ico" --add-data "certifi;certifi"  "backup_item.py"

#Backup Item (Optional)
pyinstaller --noconfirm --onefile --console --icon "img/backup_gui.ico" --add-data "certifi;certifi"  "backup_admin.py"
```
The executable will be added to a folder named 'dist' and will work on the system upon which is was built.

## TODO

 - Make backup_mgr multithreaded 
 - Make backup_mgr_gui multithreaded
 - Investigate adding in remote git support and management (i.e. )
 - Better logging throughout

## Authors

 - **Paul Skeen** - *Provided main code base*
 - **Billie Thompson** - *Provided README Template*

## Acknoledgements

Inspired by the lack of a descent solution from ESRI  for backing up AGOL content and the work carried out by [SEMCOG](https://github.com/SEMCOG/Ago_Backup)
