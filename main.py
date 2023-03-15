
from lib.sesl_cloud import *

if __name__ == '__main__':
  #-- data info
	data_src_root = 'upload/'
	download_root = 'download'
	cloud_root = "/UsrShrd/HAIS-upload_database/"
	src_file_to_download_cloud = cloud_root + "/2023-02-17-17h-04min-50sec__3D_CAMERA__42_depth.png"

	# upload a folder
	send_data(data_src_root)

	# # download a file from the cloud
	# download_data(src_file_to_download_cloud, download_root)




