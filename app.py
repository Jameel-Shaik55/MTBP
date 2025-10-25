from flask import Flask, redirect, render_template, request, session, url_for, flash, jsonify,json
import mysql.connector
import random
from send_mail import sendmail
import razorpay

RAZORPAY_KEY_ID = 'rzp_test_YxFqNpnySKudsR'
RAZORPAY_KEY_SECRET = 'Tjpe9IjAW2WBuOvlCUQ9xNUN'
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

conn = mysql.connector.connect(host="localhost", user="root", password="admin@123", database="movietickets")

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    name = request.form.get('name')
    email = request.form.get('email')
    otp = random.randint(100000, 999999)
    subject = 'Mail verification for Bookmyshow'
    body = f'''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OTP Verification</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f8f9fa; padding: 20px; }}
        .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); }}
        h2 {{ color: #007bff; }}
        p {{ font-size: 16px; color: #333; }}
        .otp {{ font-size: 24px; font-weight: bold; background: #f0f0f0; padding: 10px; display: inline-block; margin: 10px 0; }}
        .footer {{ margin-top: 20px; font-size: 12px; color: #888; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>OTP Verification</h2>
        <p>Hello,</p>
        <p>Your One-Time Password (OTP) for verification is:</p>
        <div class="otp">{otp}</div>
        <p>This OTP is valid for only 5 minutes. Do not share it with anyone.</p>
        <p>If you did not request this, please ignore this email.</p>
        <div class="footer">
            <p>Best Regards,<br>BookMyShow</p>
        </div>
    </div>
</body>
</html>
'''
    sendmail(email, subject, body)
    flash('OTP successfully sent to your mail!')
    return redirect(url_for('otp', otp=otp,email=email,name=name))


@app.route('/otp/<otp>/<email>/<name>', methods=['GET', 'POST'])
def otp(otp,email,name):
    if request.method == 'POST':
        uotp = ''.join(request.form.get(f'otp{i}') for i in range(1, 7))
        if uotp == otp:
            session['user'] = name
            session['email']=email
            return redirect(url_for('homepage'))
        else:
            flash('OTP invalid')
            return render_template('otp.html')
    return render_template('otp.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('homepage'))

@app.route('/sankranthi')
def sankranthi():
    return render_template('sankranthi.html')
@app.route('/daku')
def daku():
    return render_template('daku.html')
@app.route('/game')
def game():
    return render_template('game.html')
@app.route('/pushpa')
def pushpa():
    return render_template('pushpa.html')

@app.route('/moviehall/<movie>',methods=['GET','POST'])
def moviehall(movie):
    return render_template('moviehall.html',movie=movie)

@app.route('/seats/<movie>/<hall>/<time>',methods=['GET','POST'])
def seats(movie,hall,time):
    return render_template('seats.html',movie=movie,hall=hall,time=time)

@app.route('/get_booked_seats',)
def get_booked_seats():
    cursor = conn.cursor()
    cursor.execute("SELECT seat_numbers FROM bookings")
    booked_seats = []
    for row in cursor.fetchall():
        booked_seats.extend(map(int, row[0].split(',')))
    return jsonify({"bookedSeats": booked_seats})

@app.route('/store_seats', methods=['POST','GET'])
def store_seats():
    data = request.json
    payment_id = data.get("razorpay_payment_id")
    seat_numbers = ",".join(map(str, data.get("selectedSeats", [])))
    total_price = data.get("total_price")
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO bookings (payment_id, seat_numbers, total_price) VALUES (%s, %s, %s)"
        cursor.execute(query, (payment_id, seat_numbers, total_price))
        conn.commit()
        return jsonify({"success": True, "total_price": total_price, "message": "Seats booked successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/success',methods=['POST','GET'])
def success():
    movie = request.args.get('movie')
    hall = request.args.get('hall')
    time = request.args.get('time')
    payment_id = request.args.get('razorpay_payment_id')
    total_price= request.args.get('total_price')
    selected_seats = request.args.get('selectedSeats')
    selected_seats = json.loads(selected_seats)
    selected_seats= ",".join(map(str, selected_seats))
    subject='Movie ticket Confirmation'
    body=f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Movie Ticket Confirmation</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 20px;
                }}
                .ticket-container {{max-width: 500px; background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);align-items: center;}} h2 {{ color: #ff5722; }} .details {{align-items: center; justify-content: center;  margin-top: 15px;}} .details p {{margin: 5px 0; }} .qr-code {{margin-top: 15px; }} .footer {{margin-top: 20px;     font-size: 12px;     color: #555;}}
            </style>
        </head>
        <body>
            <div class="ticket-container">
                <h2>🎬 Movie Ticket Confirmation</h2>
                <p>Thank you for booking your movie ticket!</p>
                
                <div class="details">
                    <p><strong>Movie:</strong> { movie }</p>
                    <p><strong>Hall:</strong> { hall }</p>
                    <p><strong>Time:</strong> { time }</p>
                    <p><strong>Seats:</strong> { selected_seats }</p>
                    <p><strong>Payment ID:</strong> { payment_id }</p>
                    <p><strong>Total Price:</strong> ₹{ total_price }</p>
                </div>
        
                <div class="qr-code">
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={{ payment_id }}" alt="QR Code">
                </div>
        
                <p class="footer">Please show this ticket at the entrance. Enjoy your movie! 🍿</p>
            </div>
        </body>
        </html>
        '''
    email=session.get('email')
    sendmail(email,subject,body)
    flash('Seats Booking Successfully Done')
    return redirect(url_for('homepage'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
