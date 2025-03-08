from flask import Flask, request, redirect, jsonify
import mysql.connector
import string
import random

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='skmsAGT@12345',
        database='url_shortener'
    )

# Generate a random short code
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


#This defines the new route "/shorten" in the application.
#It only allows HTTP POST requests
@app.route('/shorten', methods=['POST'])
def shorten_url():
    #Extract data from the Request. 
    data = request.json
    long_url = data.get('long_url')
    
    if not long_url:                                   #If long_url is empty or not provided, return an error message.                 
        return jsonify({'error': 'Missing long_url'}), 400
    
    short_code = generate_short_code()                  #Creating the shortened code.
    
    with get_db_connection() as conn:                       #Establishes a connection.
        cursor = conn.cursor()                              #creates a cursor object to interact with the database.
        cursor.execute('INSERT INTO urls (long_url, short_code) VALUES (%s, %s)', (long_url, short_code))
        conn.commit()
        cursor.close()
    
    return jsonify({'short_url': request.host_url + short_code})            #Returns the shortened code.

@app.route('/<short_code>')                                 #This creates a dynamic route where short_code is a variable in the URL.
def redirect_to_url(short_code):                            
    with get_db_connection() as conn:
        cursor = conn.cursor()                              #Fetch the Original Long URL from the Database.
        cursor.execute('SELECT long_url FROM urls WHERE short_code = %s', (short_code,))
        row = cursor.fetchone()
        cursor.close()
    
    if row:
        return redirect(row[0])                             #redirect to the original long url.
    else:
        return jsonify({'error': 'Short URL not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)