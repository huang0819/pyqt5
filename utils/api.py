import requests
import logging

class Api:
    def __init__(self, url):
        self.base_url = url

    def post_data(self, data):
        is_upload = 0

        url = f'{self.base_url}/api/meals'

        payload = data['payload']

        files = [
            ('file', ('{}.npz'.format(data['file_name']), open(data['file_path'], 'rb'), 'application/octet-stream'))
        ]

        headers = {}
        try:
            response = requests.request('POST', url, headers=headers, data=payload, files=files, timeout=30)
            if response.status_code == 200:
                is_upload = 1
                logging.info('[Upload] upload success')
            else:
                logging.warning('[Upload] upload failed')

            return is_upload
        except Exception as e:
            logging.error(e)
