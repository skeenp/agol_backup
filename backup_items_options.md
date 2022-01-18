# Backup Items Script Outputs

The Backup items script (backup_items.py) extracts the data from AGOL and saves it to the backup folder. The backup includes a number of different files to represent different aspects of an item on AGOL. These are described below and can be set using the -o/--options arguement to the script. Multiple options can be specified.

## Item

This is the main json object representing an item in AGOL and contains its base information.

***Config option:*** *item*

***API Docs:*** [ArcGIS API Item](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item)

## Item Data

This option downloads data associated with the AGOL item, normally applicable to static files. Results in a blank file if no data is available to download.

***Config option:*** *data*

***API Docs:*** [ArcGIS API Download](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.download)

## Metadata

This option downloads an XML metadata document associated with the AGOL item. Results in a blank file if no data is available to download.

***Config option:*** *metadata*

***API Docs:*** [ArcGIS API Download Metadata](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.download_metadata)

## Thumbnail

This option downloads the thumbnail of the item to the thumbnail subfolder.

***Config option:*** *thumbnail*

***API Docs:*** [ArcGIS API Download Thumbnail](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.download_thumbnail)

## URL

This option creates a URL file to allow users to quickly link to the item on AGOL.

***Config option:*** *item*

***API Docs:*** [ArcGIS API Homepage](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.homepage)

## Sharing

This option creates a JSON file representing the sharing settings of the item

***Config option:*** *sharing*

***API Docs:*** [ArcGIS API Shared With](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.shared_with)

## App Info

This option captures any app info about the registered app associated with the item.

***Config option:*** *appinfo*

***API Docs:*** [ArcGIS API App Info](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.app_info)

## Related

This option documents all relationships between this item and others.

***Config option:*** *related*

***API Docs:*** [ArcGIS API Related Items](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.related_items)

## Comments

This option captures any comments associated with the item.

***Config option:*** *comments*

***API Docs:*** [ArcGIS API Item](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.comments)

## Resources

This option extracts any resources associated with the item in AGOL.

***Config option:*** *resources*

***API Docs:*** [ArcGIS API Resources](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.resources)

## Service

If supported, this option will export the service into a archive format (i.e. File GDB, Shp, etc)

***Config option:*** *service*

***API Docs:*** [ArcGIS API Export](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.export)

## All

This option selects all other options.

***Config option:*** *all*
