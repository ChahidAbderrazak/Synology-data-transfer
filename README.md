# Synology data transfer


| Function                              | Description     |
|---------------------------------------|-----------------|
|Login()                                | Initiate a new session ID.| 
|send_data(src_folder)                  | Upload all the files within the specified folder and sub-folders to the NAS file station. However, it does not upload the sub-folders itself.  | 
|download_data(src_file, dest_folder)   | Download a specific file from the NAS file station to the specified folder on your computer.| 
|Logout()                               |Terminates the session ID.|


## Execution
Step 1: Download the zip file.  
Step 2: Open the 'new_synology.py' file in the editor of your choice.  
Step 3: Enter the parameters such as Ip-address, Port #, Username, Password, src_folder_to_upload, destination_folder and src_file_to_download_cloud.  
Step 4: To upload: 'send_data(src_folder_to_upload)'  
Step 5: To download: 'download_data(src_file_to_download_cloud, destination_folder)'  

# Acknowledgement

The proposed method used some other existing preprocessing packages which were adapted with/without modifications. The main ressources are cited as follows:
* [Synology API packages](https://github.com/N4S4/synology-api)
* [Synology Guide](https://global.download.synology.com/download/Document/Software/DeveloperGuide/Package/FileStation/All/enu/Synology_File_Station_API_Guide.pdf)
