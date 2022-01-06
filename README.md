# ArcGIS Online Backup Utility

This project provides scripts and a windows exe which allows you to easily manage and schedule backups to your content on ArcGIS Online. 

## Getting Started

These instructions will give you a copy of the project to get it up and running on your local machine for development and testing purposes. See deployment for notes on deploying the project on a live system.

### Prerequisites

Requirements for the software and other tools to build, test and push 
- [Python 3](https://www.python.org/)
- [ArcGIS Online or Portal Account](https://www.arcgis.com/)

### Installing

A step by step series of examples that tell you how to get a development environment running. It is recomended to setup a virtual environment for running this project, especially if you plan to build it to and exe or equilivant file.

####Setup Virtual Environment

``` Python
    # Setup environment
    python -m venv venv
    # Activate environment
    .\venv\Scripts\activate.bat
``` 

####[Optional] Install ArcGIS API for Python with no dependancies.
This step can be handled by the requirements.txt file, however it will install the full ArcGIS API for Python which contains much more than is needed for this app. It is being managed manually here to reduce the size of files compiled for the window executable.

``` Cmd
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

This project is provided in two forms, as a windows executable and as a series of python scripts.

### Python Scripts

There are three python scripts available in the project.

#### backup_mgr.py
This tool manages backs up and ArcGIS Online item to a local folder including definitions, data and features in the requested format
```
positional arguments:
  config      Config item defining items to backup (see sample config folder)

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

### Executable

The execuatable backup_mgr.exe mirrors the definition of backup_mgr.py above.


## Building Standalong App

To build a standalone version of the app, compile with pyinstaller
``` Python
  pyinstaller --noconfirm --onefile --console --icon "./img/backup_gui.ico" --add-data "./certifi;certifi"  "./backup_mgr.py"
```
The executable will be added to a folder named 'dist' and will work on the system upon which is was built.

## TODO

 - Make backup_mgr multithreaded 
 - Add config file gui

## Authors

  - **Paul Skeen** - *Provided main code base*
  - **Billie Thompson** - *Provided README Template*

## Acknoledgements

Inspired by the lack of a descent solution from ESRI  for backing up AGOL content and the work carried out by [SEMCOG](https://github.com/SEMCOG/Ago_Backup)
