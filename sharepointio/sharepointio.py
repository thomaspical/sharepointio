from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File

import pandas as pd
import io
import os
import tempfile
from pathlib import Path
import time

class SharePointBytesIO(io.BytesIO):
    """Class to read, move, list files on Sharepoint, including Teams files folder.
    """

    def __init__(self, tenant, site, username=None, password=None, ctx_auth=None):
        """ Initialize Sharepoint connexion
        """
        # Init the BytesIO instance
        #super().__init__()
        super()

        self.tenant = tenant
        self.site = site
        self.__username = username
        self.__password = password
        self.__ctx_auth = ctx_auth

        # Connexion
        self.ctx = self._connect()

    def _connect(self, site=None):
        """Connexion to sharepoint
        """
        if site:
            self.site = site

        self.site_url = self.tenant + self.site

        # Manage authentication
        if self.__ctx_auth is None:
            if self.__username is None or self.__password is None:
                raise ValueError('Unable to authenticate, provide username+password or ctx_auth (AuthenticationContext)')
            ctx = ClientContext(self.site_url).with_user_credentials(self.__username, self.__password)
        else:
            ctx = ClientContext(self.site_url, self.__ctx_auth)

        return ctx


    def read(self, path):
        """Read file in the given path
        """
        # Fix path
        path = self._fix_path(path)

        response = File.open_binary(self.ctx, path)
        return response.content

    def list_files(self, folder, site=None, keep_only=None, start_with=None, str_contains=None):
        """List all files in a folder
        """

        if site:
            self.ctx = self._connect(site)
        
        ctx = self.ctx
        
        if os.path.basename(folder) == 'Email%20Messages':
            folder_name = [elem for elem in self.list_folders(os.path.dirname(folder)) if 'Email' in elem]
            listfolders = [os.path.join(os.path.dirname(folder), elem) for elem in folder_name]
        else:
            listfolders = [folder]

        foldx_cols = ['name', 'date_created', 'date_lastupdate', 'ServerRelativeUrl']
        foldx = pd.DataFrame(columns=foldx_cols)
        
        # fold_names = []
        # fold_time = []

        for readfolder in listfolders:
            print(readfolder)

            success_download = False
            sleeping_time = 1

            while not success_download:
                try:
                    readfolder = ctx.web.get_folder_by_server_relative_url(readfolder)
                    sub_folders = readfolder.files
                    ctx.load(sub_folders)
                    ctx.execute_query()

                    success_download = True

                except Exception as e:
                    print(e) #HTTPSConnectionPool
                    print("Failing list_folders, try again in " + str(sleeping_time) + " seconds")
                    time.sleep(sleeping_time)

                if sleeping_time > 65:
                    raise Exception("Sleeping time exceed 128 seconds.")

                sleeping_time = sleeping_time * 2






            for s_folder in sub_folders:
                # fold_names.append(s_folder.properties["Name"])
                foldx = foldx.append(pd.DataFrame([[s_folder.properties["Name"], s_folder.properties['TimeCreated'], s_folder.properties['TimeLastModified'], s_folder.properties['ServerRelativeUrl']]], columns=foldx_cols))
                print('Name: {0}'.format(s_folder.properties['Name']))
                #print('TimeCreated: {0}'.format(s_folder.properties['TimeCreated']))
                #print('TimeLastModified: {0}'.format(s_folder.properties['TimeLastModified']))

        # Keep file with extension in list
        if keep_only:
            if type(keep_only) != list:
                raise ValueError('keep_only must be a list')
            #Fix keep_only format
            for term in keep_only:
                foldx = foldx[foldx['name'].apply(lambda x: x.endswith(term))]
            # keep_only=[ '.'+elem if elem[0] != '.' else elem for elem in keep_only ]

            # fold_names=[elem for elem in fold_names if sum([elem.endswith(term) for term in keep_only]) > 0]

        # If filename start with substring
        if start_with:
            if type(start_with) != list:
                raise ValueError('start_with must be a list')
            
            for term in start_with:
                foldx = foldx[foldx['name'].apply(lambda x: x.startswith(term))]
            
            #fold_names = [elem for elem in fold_names if sum([elem.startswith(term) for term in start_with]) > 0]
        # If filename contains
        if str_contains:
            if type(str_contains) != list:
                raise ValueError('contains must be a list')

            foldx = foldx[foldx['name'].apply(lambda x: sum([term in x for term in str_contains]) > 0 )]

            #fold_names = [elem for elem in fold_names if sum([term in elem for term in str_contains]) > 0]

        return foldx.reset_index(drop=True)


    def list_folders(self, folder):
        """List all folders in a folder
        """
        ctx = self.ctx

        success_download = False
        sleeping_time = 1

        while not success_download:
            try:
                folder = ctx.web.get_folder_by_server_relative_url(folder)
                fold_names = []
                sub_folders = folder.folders
                ctx.load(sub_folders)
                ctx.execute_query()

                success_download = True

            except Exception as e:
                print(e) #HTTPSConnectionPool
                print("Failing list_folders, try again in " + str(sleeping_time) + " seconds")
                time.sleep(sleeping_time)

            if sleeping_time > 65:
                raise Exception("Sleeping time exceed 128 seconds.")

            sleeping_time = sleeping_time * 2


        for s_folder in sub_folders:
            fold_names.append(s_folder.properties["Name"])
        return fold_names


    def _fix_path(self, old_path, new_path=None):
        # Fix path format
        if new_path:
            if new_path[0] == '/':
                new_path = new_path[1:]
    
        if old_path[0] != '/':
            old_path = '/'+old_path

        # Add full URL path for old_path only.
        old_path = self.site + old_path
        
        if new_path:
            return str(old_path), str(new_path)
        else:
            return str(old_path)


    def move(self, file, old_path, new_path, site=None):
        """Move file to another directory
        """
        if site:
            self.ctx = self._connect(site)

        ctx = self.ctx

        # Add file
        old_path = old_path + '/' + file
        new_path = new_path + '/' + file

        # Fix path
        old_path, new_path = self._fix_path(old_path, new_path)

        # Move file
        source_file = ctx.web.get_file_by_server_relative_url(old_path)
        source_file.moveto(new_path, 1)
        ctx.execute_query()


    def copy(self, old_path, new_path):
        """Copy file to another directory
        """
        ctx = self.ctx

        # Fix path
        old_path, new_path = self._fix_path(old_path, new_path)

        # Move file
        source_file = ctx.web.get_file_by_server_relative_url(old_path)
        source_file.copyto(new_path, True)
        ctx.execute_query()


    def download(self, file, download_path=None, get_download_path=False):
        """Download file in a temporary directory
        """

        ctx = self.ctx
        site = self.site

        file_url = file

        if download_path == None:
            download_path = os.path.join(tempfile.mkdtemp(), os.path.basename(file_url))
        else:
            download_path = os.path.join(download_path, os.path.basename(file_url))

        success_download = False
        sleeping_time = 1

        while not success_download:
            try:
                with open(download_path, "wb") as local_file:
                    file = ctx.web.get_file_by_server_relative_url(file_url).download(local_file).execute_query()
                success_download = True

            except Exception as e:
                print(e) #HTTPSConnectionPool
                print("Failing download, try again in " + str(sleeping_time) + " seconds")
                time.sleep(sleeping_time)

            if sleeping_time > 65:
                raise Exception("Sleeping time exceed 128 seconds.")

            sleeping_time = sleeping_time * 2

        print("[Ok] file has been downloaded: {0}".format(download_path))

        if get_download_path:
            return download_path