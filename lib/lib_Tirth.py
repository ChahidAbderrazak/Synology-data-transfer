import requests
import os

# ------------------- user inputs  -------------------
ip_address = "192.168.0.198"        #Enter Synology IP-address
port = "5000"                       #Enter Synology Port #"
account_name = "xxxx" 
password = "xxxx" 
#-- data info
src_folder_to_upload = 'Synology-data-transfer-main/upload/3D_CAMERA'
destination_folder = 'Synology-data-transfer-main/download'
cloud_path = "/UsrShrd/Tirth-Patel/upload_database"
src_file_to_download_cloud = cloud_path + "/2023-02-17-17h-04min-50sec__3D_CAMERA__42_depth.png"

# ------------------------------------------------------

def login():
    _base_url = "http://" + ip_address + ":" + port + "/webapi/"
    urlLogin = _base_url + "auth.cgi"
    payloadLogin = {
        "api": "SYNO.API.Auth",
        "version": "3",
        "method": "login",
        "account": account_name,
        "passwd": password,
        "session": "FileStation",
        "format": "sid"
    }

    responseLogin = requests.post(urlLogin, data=payloadLogin)

    if responseLogin.status_code == 200:
        print("Login successful!")
    else:
        print("Login failed. Status code:", responseLogin.status_code)

    data = responseLogin.json()
    session_id = data["data"]["sid"]
    return session_id


def send_data(src_folder):
    print(f'\n --> uploading the data in : {src_folder}')

    # assign variables
    sid = login()
    _base_url = "http://" + ip_address + ":" + port + "/webapi/"

    for root, dirs, files in os.walk(src_folder):
        for file in files:
            src_folder_new = os.path.join(root, file)
            with open(src_folder_new, 'rb') as payload:
                filename = os.path.basename(src_folder_new)
                url = _base_url + "entry.cgi?api=SYNO.FileStation.Upload&version=2&method=upload&_sid=" + sid

                args = {
                    'path': cloud_path,
                    'create_parents': True,
                    'overwrite': True,
                }

                files = {'file': (filename, payload, 'application/octet-stream')}

                r = requests.post(url, data=args, files=files, verify=False)

                if r.status_code == 200 and r.json()['success']:
                    print('Upload Complete')
                else:
                    print(r.status_code, r.json())

    logout()


def download_data(src_file, dest_folder):
    print(f'\n --> downloading the data : \n - source: {src_file}  \n - destination: {dest_folder}')

    sid = login()
    _base_url = "http://" + ip_address + ":" + port + "/webapi/"
    chunk_size = 8192

    url = _base_url + "entry.cgi?api=SYNO.FileStation.Download&version=2&method=download&path=" + src_file \
          + "&_sid=" + sid

    with requests.get(url, stream=True, verify=False) as r:
        r.raise_for_status()
        if not os.path.isdir(dest_folder):
            os.makedirs(dest_folder)
        with open(dest_folder + "/" + os.path.basename(src_file), 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        if r.status_code == 200:
            print('Download Complete!')
        else:
            print(r.status_code)

    logout()


def logout():
    _base_url = "http://" + ip_address + ":" + port + "/webapi/"
    logout_api = 'auth.cgi?api=SYNO.API.Auth'
    param = {'version': 2, 'method': 'logout', 'session': "FileStation"}

    response = requests.get(_base_url + logout_api, param, verify=False)
    if response.status_code == 200 and response.json()['success']:
        print('Logout successful!')
    else:
        print(response.status_code, response.json())


if __name__ == '__main__':
    #-- data info
    data_src_root = 'upload/'
    download_root = 'download'
    cloud_root = "/UsrShrd/HAIS-upload_database/"

    src_file_to_download_cloud = cloud_root + "/2023-02-17-17h-04min-50sec__3D_CAMERA__42_depth.png"

    
    send_data(src_folder_to_upload)
    download_data(src_file_to_download_cloud, destination_folder)
