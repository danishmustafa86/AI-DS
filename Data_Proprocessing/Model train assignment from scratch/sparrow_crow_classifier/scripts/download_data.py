from kaggle.api.kaggle_api_extended import KaggleApi
import os
from pathlib import Path

def download_dataset():
    api = KaggleApi()
    api.authenticate()
    
    dataset = 'gpiosenka/100-bird-species'
    raw_data_path = Path('data/raw')
    raw_data_path.mkdir(parents=True, exist_ok=True)
    
    api.dataset_download_files(dataset, path=str(raw_data_path), unzip=True)

if __name__ == '__main__':
    download_dataset()