# Backup Admin Options

The Backup admin script (backup_admin.py) extracts data from AGOL and saves it to the backup folder. The backup includes a number of different files to represent different aspects of an item on AGOL. These are described below and can be set using the -o/--options arguement to the script. Multiple options can be specified.

## Groups

The _groups_ component exports a collection of group definitions as well as their related items as specified in -o. Each group is stored in its own folder in the _groups_ subdir and is named after the groups' GlobalID.

### Item

This is the main json object representing a group in AGOL and contains its base information.

&emsp;**_Config option:_** _item_

&emsp;**_API Docs:_** [ArcGIS API Group](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#group)

### Items

This is a json object representing all of a groups items in AGOL.

&emsp;**_Config option:_** _items_

&emsp;**_API Docs:_** [ArcGIS API Group Content](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Group.content)

### Members

This is a json object representing all members of a groups items in AGOL.

&emsp;**_Config option:_** _members_

&emsp;**_API Docs:_** [ArcGIS API Group Members](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Group.get_members)

### URL

This is the URL to the group in AGOL.

&emsp;**_Config option:_** _url_

&emsp;**_API Docs:_** [ArcGIS API Group Homepage](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Group.homepage)

### Thumbnail

This is the URL to the group in AGOL.

&emsp;**_Config option:_** _thumbnail_

&emsp;**_API Docs:_** [ArcGIS API Group Thumbnail](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.Group.get_thumbnail)

### All

This option selects all available options.

&emsp;**_Config option:_** _all_

&emsp;**_API Docs:_** _na_

## Users

The _users_ component exports a collection of user definitions as well as their related items as specified in -o. Each user is stored in its own folder in the _users_ subdir and is named after the users' GlobalID.

### Item

This is the main json object representing a user in AGOL and contains its base information.

&emsp;**_Config option:_** _item_

&emsp;**_API Docs:_** [ArcGIS API User](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#user)

### URL

This is the URL to the user in AGOL.

&emsp;**_Config option:_** _url_

&emsp;**_API Docs:_** [ArcGIS API User Homepage](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.User.homepage)

### Thumbnail

This is the URL to the user in AGOL.

&emsp;**_Config option:_** _thumbnail_

&emsp;**_API Docs:_** [ArcGIS API User Thumbnail](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.User.get_thumbnail)

### All

This option selects all available options.

&emsp;**_Config option:_** _all_

&emsp;**_API Docs:_** _na_

## Self

The _self_ component exports the current users definition and related items as specified in -o. Each user is stored in its own folder named after the users' GlobalID.

### Item

This is the main json object representing a user in AGOL and contains its base information.

&emsp;**_Config option:_** _item_

&emsp;**_API Docs:_** [ArcGIS API User](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#user)

### URL

This is the URL to the user in AGOL.

&emsp;**_Config option:_** _url_

&emsp;**_API Docs:_** [ArcGIS API User Homepage](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.User.homepage)

### Thumbnail

This is the URL to the user in AGOL.

&emsp;**_Config option:_** _thumbnail_

&emsp;**_API Docs:_** [ArcGIS API User Thumbnail](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.User.get_thumbnail)

### Groups

This is a list of groups that the user belongs to.

&emsp;**_Config option:_** _groups_

&emsp;**_API Docs:_** [ArcGIS API User Groups](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.User.groups)

### User Types

This retrieves the user type and assigned applications of the user

&emsp;**_Config option:_** _usrtypes_

&emsp;**_API Docs:_** [ArcGIS API User User Types](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.User.user_types)

### Folders

This retrieves a list of the users folders

&emsp;**_Config option:_** _folders_

&emsp;**_API Docs:_** [ArcGIS API User Folders](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.User.folders)

### Linked

This retrieves a list of the users linked accounts

&emsp;**_Config option:_** _linked_

&emsp;**_API Docs:_** [ArcGIS API User Linked Accounts](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.User.linked_accounts)

### Items

This is a json object representing all of a users items in AGOL.

&emsp;**_Config option:_** _items_

&emsp;**_API Docs:_** [ArcGIS API User Items](https://developers.arcgis.com/python/api-reference/arcgis.gis.toc.html#arcgis.gis.User.items)

### All

This option selects all available options.

&emsp;**_Config option:_** _all_

&emsp;**_API Docs:_** _na_
