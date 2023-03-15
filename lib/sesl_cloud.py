import requests
import os
# ------------------- user inputs  -------------------
ip_address = "xxx.xxx.xxx.xxx"        #Enter Synology IP-address
port = "xxxx"                       #Enter Synology Port #"
account_name = "xxxx" 
password = "xxx"
#-- data info
data_src_root = 'upload/'
download_root = 'download'
cloud_root = "/UsrShrd/HAIS-upload_database/"

src_file_to_download_cloud = cloud_root + "/2023-02-17-17h-04min-50sec__3D_CAMERA__42_depth.png"
# ------------------------------------------------------
try:
    from lib.credentials import *
except:
    from credentials import *

_base_url = "http://" + ip_address + ":" + port + "/webapi/"

def get_api_list():
    query_path = 'query.cgi?api=SYNO.API.Info'
    list_query = {'version': '1', 'method': 'query', 'query': 'all'}
    response = requests.get(_base_url + query_path, list_query, verify=False).json()
    full_api_list=response['data']
    # print(f'\n - full_api_list={full_api_list}')
    return  full_api_list 

def login():
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

def _get_error_code(response) -> int:
    if response.get('success'):
        code = 0
    else:
        code = response.get('error').get('code')
    return code

def send_request(api_name, api_path, req_param, method='get'):  # 'post' or 'get'
    global  _sid, file_station_list

    # Convert all boolean in string in lowercase because Synology API is waiting for "true" or "false"
    for k, v in req_param.items():
        if isinstance(v, bool):
            req_param[k] = str(v).lower()

    if method is None:
        method = 'get'

    req_param['_sid'] = _sid

    url = ('%s%s' % (_base_url, api_path)) + '?api=' + api_name

    if method == 'get':
        response = requests.get(url, req_param, verify=True)
    elif method == 'post':
        response = requests.post(url, req_param, verify=True)

    error_code = _get_error_code(response.json())

    if error_code:
        print('Data request failed: error code ' + str(error_code))
    
    return response.json()
        
def create_folder_set_API(folder_path, name, additional=None):
    api_name = 'SYNO.FileStation.CreateFolder'
    info = file_station_list[api_name]
    api_path = info['path']
    req_param = {'version': 2, 'method': 'create'}

    for key, val in locals().items():
        if key not in ['self', 'api_name', 'info', 'api_path', 'req_param', 'folder_path', 'additional', 'name']:
            if val is not None:
                req_param[str(key)] = val

    if type(folder_path) is list:
        new_path = []
        [new_path.append('"' + x + '"') for x in folder_path]
        folder_path = new_path
        folder_path = '[' + ','.join(folder_path) + ']'
        req_param['folder_path'] = folder_path
    elif folder_path is not None:
        req_param['folder_path'] = folder_path
    else:
        return 'Enter a valid path'

    if type(name) is list:
        new_path = []
        [new_path.append('"' + x + '"') for x in name]
        name = new_path
        name = '[' + ','.join(name) + ']'
        req_param['name'] = name
    elif name is not None:
        req_param['name'] = '"' + name + '"'
    else:
        return 'Enter a valid path'

    if additional is None:
        additional = ['real_path', 'size', 'owner', 'time']

    if type(additional) is list:
        additional = ','.join(additional)

    req_param['additional'] = additional

    return send_request(api_name, api_path, req_param) 

def upload_subfolder_file(url, file_path, cloud_dst_folder):

    print(f'\n - uploading to NAS: \n\t - file path={file_path},  \n\t - destination folder ={cloud_dst_folder}')
    with open(file_path, 'rb') as payload:
        filename = os.path.basename(file_path)

        args = {
            'path': cloud_dst_folder,
            'create_parents': True,
            'overwrite': True,
        }

        files = {'file': (filename, payload, 'application/octet-stream')}

        r = requests.post(url, data=args, files=files, verify=False)

        if r.status_code == 200 and r.json()['success']:
            print('Upload Complete')
            return 0
        else:
            print(r.status_code, r.json())
            return 1



def send_data(src_folder):
    global  _sid, file_station_list
    file_station_list, _sid =get_api_list(), login()
    url = _base_url + "entry.cgi?api=SYNO.FileStation.Upload&version=2&method=upload&_sid=" + _sid
    
    for root, dirs, files in os.walk(src_folder):
        print(f'\n --> uploading the subfolder: {dirs}')
        for file in files:
            file_path = os.path.join(root, file)
            # create subfolder folder a
            subfolder_path=root[len(data_src_root):] 
            # create the 
            cloud_dst_folder= os.path.join(cloud_root, subfolder_path )
            dst_folder, dst_subfolder=os.path.dirname(cloud_dst_folder), os.path.basename(cloud_dst_folder)
            create_folder_set_API(dst_folder, dst_subfolder)
            # upload file
            cloud_dst_folder= os.path.join(cloud_root, subfolder_path )
            upload_subfolder_file(url, file_path, cloud_dst_folder)
    logout()


def download_data(src_file, dest_folder):
    global  _sid, file_station_list
    file_station_list, _sid =get_api_list(), login()
    print(f'\n --> downloading the data : \n - source: {src_file}  \n - destination: {dest_folder}')
    chunk_size = 8192

    url = _base_url + "entry.cgi?api=SYNO.FileStation.Download&version=2&method=download&path=" + src_file \
          + "&_sid=" + _sid

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
    
    # upload a folder
    send_data(data_src_root)

    # # download a file from the cloud
    # download_data(src_file_to_download_cloud, download_root)

    # # create a folder on the cloud
    # folder_path = "/UsrShrd/Tirth-Patel"
    # subfolder_name = "test"
    # create_folder_set_API(folder_path, subfolder_name)

