import shutil
from pathlib import Path

def prepare_data():
    # Create processed directories
    processed_path = Path('data/processed')
    (processed_path/'train/sparrow').mkdir(parents=True, exist_ok=True)
    (processed_path/'train/crow').mkdir(parents=True, exist_ok=True)
    (processed_path/'test/sparrow').mkdir(parents=True, exist_ok=True)
    (processed_path/'test/crow').mkdir(parents=True, exist_ok=True)
    
    def copy_images(src_pattern, dest_dir):
        for img_path in Path('data/raw').glob(src_pattern):
            shutil.copy(img_path, f'data/processed/{dest_dir}/{img_path.name}')
    
    # Copy images
    copy_images('train/SPARROW/*.jpg', 'train/sparrow')
    copy_images('train/CROW/*.jpg', 'train/crow')
    copy_images('test/SPARROW/*.jpg', 'test/sparrow')
    copy_images('test/CROW/*.jpg', 'test/crow')

if __name__ == '__main__':
    prepare_data()