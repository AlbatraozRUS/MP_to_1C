import json
import os
from io import BytesIO

from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload

class LicenseGDriveChecker:
	__FILE_ID__ = "1e6ET1Tl7c1PdwAq0o95iwmZzSOmjRXyN"

	def __init__(self) -> None:
		credentials = service_account.Credentials.from_service_account_file(
			os.path.join(os.path.dirname(__file__), 'drive_token.json'),
			scopes=['https://www.googleapis.com/auth/drive'])
		self.__service__ = build('drive', 'v3', credentials=credentials)


	def __download_file__(self):
		file_content = self.__service__.files().get_media(fileId=self.__FILE_ID__).execute()
		self.__license_data__ = json.loads(file_content)


	def __check_validity__(self, license_key):		
		for license in self.__license_data__:
			if license['key'] == license_key:
				return license['valid']
		return False
	

	def __activate_license__(self):
		license_data = {'valid': True}
		license_file_path = os.path.join('C:\\',
										 'Program Files',
										 'creds.json')
		os.makedirs(os.path.dirname(license_file_path), exist_ok=True)
		with open(license_file_path, 'w') as f:
			json.dump(license_data, f)
		   
		os.system(f'attrib +h "{license_file_path}"')
		
	

	def check_active_license(self):
		license_file_path = os.path.join('C:\\',
										 'Program Files',
										 'creds.json')
		if os.path.exists(license_file_path):
			with open(license_file_path, 'r') as f:
				license_data = json.load(f)
				if license_data['valid'] is True:
					return True
		return False


	def check_license(self, license_key):
		self.__download_file__()

		if not self.__check_validity__(license_key):
			return False
		
		for license in self.__license_data__:
			if license['key'] == license_key:
				self.__activate_license__()
				license['valid'] = False
				break

		bytes_io = BytesIO()
		bytes_io.write(json.dumps(self.__license_data__).encode('utf-8'))
		bytes_io.seek(0)
	
		media = MediaIoBaseUpload(bytes_io, mimetype='text/plain', resumable=True)
		res = self.__service__.files().update(fileId=self.__FILE_ID__,
											  media_body=media).execute()

		return res

