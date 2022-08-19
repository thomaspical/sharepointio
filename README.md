SharepointIO
=============

An easy use of Office365-REST-Python-Client to download/upload/list sharepoint files

**********
How to use
**********

Init sharepoint connexion
*************************

from sharepointio import sharepointio

tenant = 'https://mypersonnal.sharepoint.com'

site = '/sites/12345-MyTeams-Channel'

sharepoint = sharepointio.SharePointBytesIO(tenant, site, username=USERNAME, password=PASSWORD)

********
Commands
********

**sharepoint.read(path)** : 
Read file in the given path

**sharepoint.list_files(folder, site=None, keep_only=None, start_with=None, str_contains=None)** :
List all files in a folder. Output is a Pandas dataframe.

**sharepoint.list_folders(folder)** :
List all folders in a folder

**sharepoint.move(file, old_path, new_path, site=None)** :
Move file to another directory

**sharepoint.copy(old_path, new_path)** :
Copy file to another directory

**sharepoint.download(file, download_path=None, get_download_path=False)** :
Download file in a temporary directory

**********
Changelog
**********
**0.0.4**
- Update list_files : add security in case of max rate exceeded
- Update list_folder : add security in case of max rate exceeded

**0.0.3**
- Update download : Error handling due to too many attempts has been incorporated. Bugs have been fixed.

**0.0.2** :

- Update list_files : Automatically read all "Email%20Messages" folders received on Sharepoint when a new folder is automatically created by Sharepoint. The function outputs a pandas table with the following fields : name, date_created, date_lastupdate, ServerRelativeUrl
- Update download : new field full_URL, allows to pass the links of the ServerRelativeUrl field in list_files. 

*******
License
*******

SharepointIO is licensed under the Apache 2.0 license.