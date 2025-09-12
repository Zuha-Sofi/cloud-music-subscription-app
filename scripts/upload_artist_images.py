import boto3
import json
import requests
import os
from botocore.exceptions import ClientError

s3 = boto3.client('s3', region_name='us-east-1')

bucket_name = 's3993780bucket' 


def create_bucket():
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"S3 bucket '{bucket_name}' created.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"S3 bucket '{bucket_name}' already exists.")
        else:
            raise

def download_and_upload_images():
    with open('2025a1.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    os.makedirs('images', exist_ok=True)

    image_urls = set(song['img_url'] for song in data['songs'])
    print(f"Downloading {len(image_urls)} artist images")

    for url in image_urls:
        file_name = url.split('/')[-1]
        file_path = f'images/{file_name}'

        # Downloading image
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {file_name}")

            # Uploading to S3
            s3.upload_file(file_path, bucket_name, file_name)
            print(f"Uploaded to S3: {file_name}")
        else:
            print(f"Failed to download {file_name}")

    print("All images successfully uploaded to S3.")

if __name__ == '__main__':
    create_bucket()
    download_and_upload_images()