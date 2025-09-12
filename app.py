from flask import Flask, render_template, request, redirect, url_for, session
import boto3

app = Flask(__name__)
app.secret_key = '0wk7kSUe2RiXwC3XWM+oDmC7dS9GbgbvsXAkgfKp'  # Change this to a strong secret key

# AWS DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
login_table = dynamodb.Table('login')
music_table = dynamodb.Table('music')
subscription_table = dynamodb.Table('subscription')

# AWS S3 Client (for future extension if needed)
s3 = boto3.client('s3', region_name='us-east-1')
BUCKET_NAME = 'your-s3-bucket-name-here'  # Replace with your real S3 bucket name

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

    # Fetch user's subscriptions
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

    title = request.form.get('title').strip()
    artist = request.form.get('artist').strip()
    year = request.form.get('year').strip()
    album = request.form.get('album').strip()

    # At least one field must be filled
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

    scan_kwargs = {
        'FilterExpression': filter_conditions[0]
    }
    for cond in filter_conditions[1:]:
        scan_kwargs['FilterExpression'] = scan_kwargs['FilterExpression'] & cond

    # Scan music table
    response = music_table.scan(**scan_kwargs)
    results = response['Items']

    # Fetch user's current subscriptions
    subscription_response = subscription_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(session['email'])
    )
    subscriptions = subscription_response['Items']

    if not results:
        return render_template('main.html', username=session['username'], subscriptions=[subscriptions], results=[], message="No result is retrieved. Please query again.")

    return render_template('main.html', username=session['username'], subscriptions=subscriptions, results=results)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
