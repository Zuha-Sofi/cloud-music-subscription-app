import boto3
import json
import requests
import os
from botocore.exceptions import ClientError

# Configure AWS credentials via ~/.aws/credentials or environment variables
s3 = boto3.client('s3', region_name='us-east-1')

# Replace with your actual bucket name when running locally
BUCKET_NAME = "<your-s3-bucket-name>"


def create_bucket(bucket_name=BUCKET_NAME):
    """
    Creates an S3 bucket if it does not already exist.
    """
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f" S3 bucket '{bucket_name}' created.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f" S3 bucket '{bucket_name}' already exists.")
        elif e.response['Error']['Code'] == 'BucketAlreadyExists':
            print(f" Bucket name '{bucket_name}' is already taken globally. Please use a unique name.")
        else:
            raise


def download_and_upload_images(json_file="data/2025a1.json", bucket_name=BUCKET_NAME):
    """
    Downloads artist images from URLs in the JSON file and uploads them to the specified S3 bucket.
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    os.makedirs('images', exist_ok=True)

    image_urls = set(song['img_url'] for song in data['songs'])
    print(f" Downloading {len(image_urls)} artist images...")

    for url in image_urls:
        file_name = url.split('/')[-1]
        file_path = os.path.join('images', file_name)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f" Downloaded: {file_name}")

            # Uploading to S3
            s3.upload_file(file_path, bucket_name, file_name)
            print(f" Uploaded to S3: {file_name}")
        except Exception as e:
            print(f" Failed for {url}: {e}")

    print(" All images processed and uploaded to S3.")


# ---------- Main Execution ----------
if __name__ == '__main__':
    create_bucket()
    download_and_upload_images()
