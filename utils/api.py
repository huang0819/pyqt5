import requests
import logging

class Api:
    def __init__(self, url):
        self.base_url = url

    def upload_data(self, data):
        """
        post collected data
        :param data:
            user_id: int
            weight: float
            meal_date: string
            type: int
            file: npz
        :return: is_upload (int)
        """
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
                logging.info(f'[API] {url} success')
            else:
                logging.warning(f'[API] {url} failed')

            return is_upload
        except Exception as e:
            logging.error(e)

    def fetch_schools(self):
        url = f'{self.base_url}/api/schools'

        payload = {}
        headers = {}

        schools = []

        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                schools = response.json()['data']['schools']
                logging.info(f'[API] {url} success')
            else:
                logging.warning(f'[API] {url} failed')

            return schools
        except Exception as e:
            logging.error(e)

    def fetch_user_list(self, school_id=None, grade=None, class_name=None):
        url = f'{self.base_url}/api/profileList'

        query = []
        if school_id is not None:
            query.append(f'school_id={school_id}')

        if grade is not None:
            query.append(f'grade={grade}')

        if class_name is not None:
            query.append(f'class={class_name}')

        if len(query) != 0:
            url = url + f"?{'&'.join(query)}"

        payload = {}
        headers = {}

        user_list = []
        status_code = 0

        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            status_code = response.status_code
            if response.status_code == 200:
                user_list = response.json()['data']['profiles']
                logging.info(f'[API] {url} success')
            else:
                logging.warning(f'[API] {url} failed')
        except Exception as e:
            logging.error(e)

        return status_code, user_list
