# /usr/bin/python3

from arcgis.gis import GIS
import logging

EXPORT_FORMATS = {
    "csv": "CSV",
    "shp": "Shapefile",
    "geojson": "GeoJson",
    "fgdb": "File Geodatabase",
    "gpkg": "geoPackage",
    "kml": "KML",
    "spkg": "Scene Package",
    "vtpk": "Vector Tile Package",
    "xls": "Excel",
    "none": None,
}


class Agol:
    _logger = None
    _gis = None
    _error = None

    def __init__(self, portal: str, uname: str, pword: str, logger: logging):
        # Get logger
        self._logger = logger
        # Connect to portal
        try:
            # Connect to portal, collecting connection
            self._gis = GIS(portal, uname, pword)
            # Provide success
            self._logger.info(f"Connected to {portal}")
        except ConnectionRefusedError:
            # Provide connection error
            self._error = "Cannot validate the supplied AGOL portal URL."
            msg = "Cannot connect to supplied portal"
            self._logger.exception(msg)
        except Exception as ex:
            # Provide generic error
            self._error = f"Cannot connect to portal.\n{str(ex)}"
            msg = "Error authenticating while connecting to portal"
            self._logger.exception(msg)

    @property
    def gis(self):
        # Return gis
        return self._gis

    @property
    def error(self):
        # Return errors
        return self._error
