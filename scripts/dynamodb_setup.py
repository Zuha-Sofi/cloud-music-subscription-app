
import boto3
import json
from botocore.exceptions import ClientError

# Setting up the DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# ---------- Task 1.1: Creating login table and inserting 10 users ----------
def create_login_table():
    table_name = 'login'
    try:
        table = dynamodb.Table(table_name)
        table.load()
        print(f"Table '{table_name}' already exists.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            try:
                table = dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
                    AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
                    BillingMode='PAY_PER_REQUEST'
                )
                print("Creating login table...")
                table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
                print("Login table created.")
            except ClientError as ce:
                print("Failed to create table:", ce.response['Error']['Message'])
                return
        else:
            raise

    # Inserting 10 login items
    table = dynamodb.Table(table_name)
    student_id = 's3123456'
    name = 'student'

    for i in range(10):
        email = f"{student_id}{i}@student.rmit.edu.au"
        user_name = f"{name}{i}"
        password = f"{i}01234{i}"
        table.put_item(Item={
            'email': email,
            'user_name': user_name,
            'password': password
        })
    print("10 login users inserted.")

# ---------- Step 1: Create music table ----------
def create_music_table():
    table_name = 'music'
    try:
        table = dynamodb.Table(table_name)
        table.load()
        print(f"Table '{table_name}' already exists.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            try:
                table = dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {'AttributeName': 'title', 'KeyType': 'HASH'},
                        {'AttributeName': 'album', 'KeyType': 'RANGE'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'title', 'AttributeType': 'S'},
                        {'AttributeName': 'album', 'AttributeType': 'S'}
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                print("Creating music table...")
                table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
                print("Music table created.")
            except ClientError as ce:
                print("Failed to create table:", ce.response['Error']['Message'])
                return
        else:
            raise

# ---------- Step 2: Load data from JSON file ----------
def load_music_data():
    table = dynamodb.Table('music')

    try:
        with open('2025a1.json', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: '2025a1.json' not found.")
        return
    except json.JSONDecodeError as je:
        print("Error reading JSON:", je)
        return

    songs = data.get('songs', [])
    print(f"Loading {len(songs)} songs into the music table...")

    for i, song in enumerate(songs, start=1):
        try:
            item = {
                'title': song['title'],
                'album': song['album'],
                'artist': song['artist'],
                'year': int(song['year']),
                'image_url': song['img_url']
            }
            table.put_item(Item=item)

            if i % 10 == 0 or i == len(songs):
                print(f"Inserted {i}/{len(songs)} songs")

        except Exception as e:
            print(f"Skipped song at index {i - 1}: {e}")

    print("All valid songs inserted successfully.")

# ---------- Task 1.4: Creating subscription table ----------
def create_subscription_table():
    table_name = 'subscription'
    try:
        table = dynamodb.Table(table_name)
        table.load()
        print(f"Table '{table_name}' already exists.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            try:
                table = dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {'AttributeName': 'email', 'KeyType': 'HASH'},
                        {'AttributeName': 'title', 'KeyType': 'RANGE'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'email', 'AttributeType': 'S'},
                        {'AttributeName': 'title', 'AttributeType': 'S'}
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
                print("Creating subscription table...")
                table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
                print("Subscription table created.")
            except ClientError as ce:
                print("Failed to create table:", ce.response['Error']['Message'])
                return
        else:
            raise

if __name__ == '__main__':
    create_login_table()
    create_music_table()
    load_music_data()
    create_subscription_table()
