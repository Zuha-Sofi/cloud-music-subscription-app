from flask import Flask, render_template, request, redirect, url_for, session
import boto3
import os

app = Flask(__name__)
# Use environment variable for secret key
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'replace-with-a-secure-key')

# AWS DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
login_table = dynamodb.Table(os.getenv('LOGIN_TABLE', 'login'))
music_table = dynamodb.Table(os.getenv('MUSIC_TABLE', 'music'))
subscription_table = dynamodb.Table(os.getenv('SUBSCRIPTION_TABLE', 'subscription'))

# AWS S3 Client (optional)
s3 = boto3.client('s3', region_name='us-east-1')
BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'your-s3-bucket-name-here')

# Route for Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        response = login_table.get_item(Key={'email': email})
        user = response.get('Item')

        if user and user['password'] == password:
            session['email'] = email
            session['username'] = user['user_name']
            return redirect(url_for('main_page'))
        else:
            error = "Email or password is invalid"
    return render_template('login.html', error=error)

# Route for Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        response = login_table.get_item(Key={'email': email})
        user = response.get('Item')

        if user:
            error = "The email already exists"
        else:
            login_table.put_item(Item={
                'email': email,
                'user_name': username,
                'password': password
            })
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

# Route for Main Page
@app.route('/main', methods=['GET'])
def main_page():
    if 'email' not in session:
        return redirect(url_for('login'))

    user_email = session['email']
    username = session['username']

    response = subscription_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(user_email)
    )
    subscriptions = response['Items']

    return render_template('main.html', username=username, subscriptions=subscriptions)

# Subscribe to a song
@app.route('/subscribe', methods=['POST'])
def subscribe():
    if 'email' not in session:
        return redirect(url_for('login'))

    title = request.form['title']
    artist = request.form['artist']
    year = request.form['year']
    album = request.form['album']
    image_url = request.form['image_url']

    subscription_table.put_item(Item={
        'email': session['email'],
        'title': title,
        'artist': artist,
        'year': year,
        'album': album,
        'image_url': image_url
    })
    return redirect(url_for('main_page'))

# Remove a subscribed song
@app.route('/remove', methods=['POST'])
def remove():
    if 'email' not in session:
        return redirect(url_for('login'))

    title = request.form['title']

    subscription_table.delete_item(
        Key={
            'email': session['email'],
            'title': title
        }
    )
    return redirect(url_for('main_page'))

# Query Music Table
@app.route('/query', methods=['POST'])
def query():
    if 'email' not in session:
        return redirect(url_for('login'))

    title = request.form.get('title', '').strip()
    artist = request.form.get('artist', '').strip()
    year = request.form.get('year', '').strip()
    album = request.form.get('album', '').strip()

    if not (title or artist or year or album):
        subscription_response = subscription_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(session['email'])
        )
        subscriptions = subscription_response['Items']
        return render_template('main.html', username=session['username'], subscriptions=subscriptions, results=[], message="Please fill at least one field to query.")

    filter_conditions = []

    if title:
        filter_conditions.append(boto3.dynamodb.conditions.Attr('title').contains(title))
    if artist:
        filter_conditions.append(boto3.dynamodb.conditions.Attr('artist').contains(artist))
    if year:
        try:
            filter_conditions.append(boto3.dynamodb.conditions.Attr('year').eq(int(year)))
        except ValueError:
            subscription_response = subscription_table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(session['email'])
            )
            subscriptions = subscription_response['Items']
            return render_template('main.html', username=session['username'], subscriptions=subscriptions, results=[], message="Year must be a number.")
    if album:
        filter_conditions.append(boto3.dynamodb.conditions.Attr('album').contains(album))

    scan_kwargs = {'FilterExpression': filter_conditions[0]}
    for cond in filter_conditions[1:]:
        scan_kwargs['FilterExpression'] &= cond

    response = music_table.scan(**scan_kwargs)
    results = response['Items']

    subscription_response = subscription_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(session['email'])
    )
    subscriptions = subscription_response['Items']

    if not results:
        return render_template('main.html', username=session['username'], subscriptions=subscriptions, results=[], message="No result is retrieved. Please query again.")

    return render_template('main.html', username=session['username'], subscriptions=subscriptions, results=results)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
