import boto3
import json
import botocore.exceptions

# Set up the DynamoDB client
# Make sure your AWS credentials are configured in ~/.aws/credentials or via environment variables
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# ---------- Task 1.1: Create login table and insert 10 users ----------
def create_login_table(student_id="sXXXXXXX", name="FirstnameLastname"):
    """
    Creates the 'login' table and inserts 10 test users.
    Replace the default student_id and name values with your own when running locally.
    """
    try:
        table = dynamodb.create_table(
            TableName='login',
            KeySchema=[
                {'AttributeName': 'email', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("Creating login table...")
        table.meta.client.get_waiter('table_exists').wait(TableName='login')
        print("Login table created.")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(" Login table already exists.")
        else:
            raise

    # Insert 10 login items (sample/demo data only)
    table = dynamodb.Table('login')
    for i in range(10):
        email = f"{student_id}{i}@student.rmit.edu.au"
        user_name = f"{name}{i}"
        password = f"{i}01234{i}"
        table.put_item(Item={
            'email': email,
            'user_name': user_name,
            'password': password
        })
    print(" 10 login users inserted (sample data).")

# ---------- Task 1.2: Create music table ----------
def create_music_table():
    try:
        table = dynamodb.create_table(
            TableName='music',
            KeySchema=[
                {'AttributeName': 'title', 'KeyType': 'HASH'},
                {'AttributeName': 'artist', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'title', 'AttributeType': 'S'},
                {'AttributeName': 'artist', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(" Creating music table...")
        table.meta.client.get_waiter('table_exists').wait(TableName='music')
        print(" Music table created.")
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(" Music table already exists.")
        else:
            raise

# ---------- Task 1.3: Load music data from JSON ----------
def load_music_data(json_file="data/2025a1.json"):
    """
    Loads music data from a JSON file into the 'music' DynamoDB table.
    """
    table = dynamodb.Table('music')
    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)

    songs = data['songs']
    print(f" Loading {len(songs)} songs into the music table...")

    for i, song in enumerate(songs):
        item = {
            'title': song['title'],
            'artist': song['artist'],
            'year': int(song['year']),
            'album': song['album'],
            'image_url': song['img_url']
        }
        table.put_item(Item=item)
        if (i + 1) % 10 == 0:
            print(f" Inserted {i + 1} songs...")

    print(" All songs inserted into music table.")

# ---------- Main execution ----------
if __name__ == '__main__':
    # Replace with your details only when running locally
    create_login_table(student_id="sXXXXXXX", name="FirstnameLastname")
    create_music_table()
    load_music_data()
