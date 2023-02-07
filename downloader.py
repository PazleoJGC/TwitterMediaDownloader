import requests
import os

class Downloader:
    def download(file_url : str, file_path : str):
        res = requests.get(file_url)
        if res.status_code == 200:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as file_handle:
                file_handle.write(res.content)
            return [True, res.status_code]
        else:
            return [False, res.status_code]