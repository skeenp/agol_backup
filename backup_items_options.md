# Backup Item Options

The Backup items script (backup_items.py) extracts data from AGOL and saves it to the backup folder. The backup includes a number of different files to represent different aspects of an item on AGOL. These are described below and can be set using the -o/--options arguement to the script. Multiple options can be specified.

## Item

This is the main json object representing an item in AGOL and contains its base information.

&emsp;***Config option:&emsp;*** *item*

&emsp;***API Docs:&emsp;*** [ArcGIS API Item](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item)

## Item Data

This option downloads data associated with the AGOL item, normally applicable to static files. Results in a blank file if no data is available to download.

&emsp;***Config option:&emsp;*** *data*

&emsp;***API Docs:&emsp;*** [ArcGIS API Download](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.download)

## Metadata

This option downloads an XML metadata document associated with the AGOL item. Results in a blank file if no data is available to download.

&emsp;***Config option:&emsp;*** *metadata*

&emsp;***API Docs:&emsp;*** [ArcGIS API Download Metadata](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.download_metadata)

## Thumbnail

This option downloads the thumbnail of the item to the thumbnail subfolder.

&emsp;***Config option:&emsp;*** *thumbnail*

&emsp;***API Docs:&emsp;*** [ArcGIS API Download Thumbnail](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.download_thumbnail)

## URL

This option creates a URL file to allow users to quickly link to the item on AGOL.

&emsp;***Config option:&emsp;*** *item*

&emsp;***API Docs:&emsp;*** [ArcGIS API Homepage](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.homepage)

## Sharing

This option creates a JSON file representing the sharing settings of the item

&emsp;***Config option:&emsp;*** *sharing*

&emsp;***API Docs:&emsp;*** [ArcGIS API Shared With](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.shared_with)

## App Info

This option captures any app info about the registered app associated with the item.

&emsp;***Config option:&emsp;*** *appinfo*

&emsp;***API Docs:&emsp;*** [ArcGIS API App Info](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.app_info)

## Related

This option documents all relationships between this item and others.

&emsp;***Config option:&emsp;*** *related*

&emsp;***API Docs:&emsp;*** [ArcGIS API Related Items](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.related_items)

## Comments

This option captures any comments associated with the item.

&emsp;***Config option:&emsp;*** *comments*

&emsp;***API Docs:&emsp;*** [ArcGIS API Item](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.comments)

## Resources

This option extracts any resources associated with the item in AGOL.

&emsp;***Config option:&emsp;*** *resources*

&emsp;***API Docs:&emsp;*** [ArcGIS API Resources](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.resources)

## Service

If supported, this option will export the service into a archive format (i.e. File GDB, Shp, etc)

&emsp;***Config option:&emsp;*** *service*

&emsp;***API Docs:&emsp;*** [ArcGIS API Export](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Item.export)

## All

This option selects all available options.

&emsp;***Config option:&emsp;*** *all*

&emsp;***API Docs:*** *na*