#Name of programmer: Fiorella Scarpino 
#Student ID: 21010043
#Date: 1/05/2022
#Final Version. Created with Flask Python
#Description of program: The main app where the data is processed. 

from flask import Flask, flash, render_template, request, session, redirect, url_for, make_response
import mysql.connector, dbconn
from wtforms import Form, StringField, BooleanField, validators,PasswordField, DateField, IntegerField
from datetime import datetime,date
import time
from passlib.hash import sha256_crypt
from functools import wraps
from collections import Counter
import calendar
import json

app = Flask(__name__)
app.config['SECRET_KEY']= 'f84LeUyqvBugOaiiduQOpg' 



class RegisterForm(Form):
    firstname = StringField('First Name',[validators.DataRequired(),validators.Length(min=2, max=45)])
    lastname = StringField('Last Name',[validators.DataRequired(),validators.Length(min=2, max=45)])
    email = StringField('Email',[validators.DataRequired(),validators.Length(min=6, max=35)])
    password = PasswordField('Password',[validators.DataRequired(),validators.EqualTo('confirm',message='Password must match')])
    confirm = PasswordField('Confirm Pass')

class LoginForm(Form):
    email = StringField('Email',[validators.Length(min=6,max=35)])
    password = PasswordField('Password')

@app.route('/')
def index():
    return render_template('Home.html')

@app.route('/room')
def room():
    return render_template('Room.html')

@app.route('/ourlocations')
def ourlocations():
    return render_template('ourLocations.html')

@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    formLogin = LoginForm(request.form)
    conn = dbconn.getConnection()
    cursor = conn.cursor()
    if request.method == 'POST' and formLogin.validate():
        email = formLogin.email.data
        password = formLogin.password.data
        userLoginData = cursor.execute("SELECT * FROM user WHERE email = (%s);",[email])
        userLoginData = cursor.fetchall()
        if userLoginData: #if login details are valid
            userLoginDataArray = []
        
            for row in userLoginData:#prints the result of the select query into the array
                for item in row:
                    userLoginDataArray.append(item)
                hash = userLoginDataArray[4]
                if userLoginDataArray[3] == email and sha256_crypt.verify(request.form['password'], hash):
                    if userLoginDataArray[5] == "standard":
                        session['login'] = True
                        session['email'] = userLoginDataArray[3]
                        session['user'] = 'standard'
                        session['userid'] = userLoginDataArray[0]
                        return redirect('homepage')
                    if userLoginDataArray[5] == "admin":
                        session['login'] = True
                        session['email'] = userLoginDataArray[3]
                        session['user'] = 'admin'
                        session['admin'] = True
                        return redirect('adminHomepage')
                else:
                    error = 'Invalid email and/or password'
            cursor.close()
            conn.close()
        else:
            error = 'Invalid email and/or password'
            return render_template('/Login.html',formlogin=formLogin,error=error)    
    return render_template('/Login.html',formlogin=formLogin,error=error)
    
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('email') is None or session.get('login') is False:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/homepage', methods=["GET","POST"]) #user homepage
@login_required
def homepage():
    if "email" in session and "user" in session and "userid" in session:
        conn = dbconn.getConnection()
        cursor = conn.cursor()
        email = session["email"] 
        user = session["user"]
        userid = session["userid"]
        cancelMessage = ""
        toPay = False
    
        #SHOW ALL BOOKINGS
        bookingUser= []#gets data from the customers reservations
        cursor.execute("SELECT * FROM customerreservation WHERE idUserReservation = (%s);",[userid],)
        bookingsUserSQL = cursor.fetchall()
        for row in bookingsUserSQL:
            tempRow = [row[0],row[1],row[2]]
            bookingUser.append(tempRow)
    
        reservationElement = []#gets data from reservations (checkin,checkout etc)
        for reservation_element in bookingUser:
            bookingSelected = reservation_element[2]
            reservationUserSQL = cursor.execute("SELECT * FROM reservation WHERE idReservation = (%s);",(bookingSelected,))
            reservationUserSQL = cursor.fetchall()
            guestResSQL = cursor.execute("SELECT * FROM guestinformation WHERE idReservation = (%s);",(bookingSelected,))
            guestResSQL = cursor.fetchall()
            for row in reservationUserSQL:
                for rowGuest in guestResSQL:
                    cursor.execute("SELECT hotelCity FROM hotel WHERE idHotel = (%s);",(row[1],)) #gets city name
                    hotelReservationSQL = cursor.fetchall()
                    hotelReservationSQL=[i[0] for i in hotelReservationSQL]
                    tempReservation = [row[0],hotelReservationSQL[0],row[2],row[3],rowGuest[2],row[4],rowGuest[3],rowGuest[4]]#appends data that customer will see into an array
                    reservationElement.append(tempReservation)
                
        #CANCEL BOOKING
        if "Continue": #if button pressed
            if 'bookingchoice' in request.form: # if radio button pressed
                request_bookingchoice = request.form['bookingchoice']
                userCancelationChoice = request_bookingchoice.split()
                outDateValid= datetime.strptime(str(reservationElement[0][3]), "%Y-%m-%d") #validates the date
                nowDate= date.today()#todays date
                strNow = str(nowDate)
                todaysDate = time.strptime(strNow,'%Y-%m-%d')
                tempToday = "{year}-{month}-{day}".format(year=todaysDate[0],month=todaysDate[1],day=todaysDate[2])
                today = datetime.strptime(str(tempToday), "%Y-%m-%d")

                advancedCancelDate = datetime.strptime(str(reservationElement[0][3]), '%Y-%m-%d') - datetime.strptime(str(tempToday), '%Y-%m-%d')	
                advancedCancelDate = advancedCancelDate.days
                cursor.execute("SELECT customerPrice FROM guestinformation WHERE idReservation = (%s);",(reservationElement[0][0],))
                customerPriceSQL = cursor.fetchall()
                customerPriceFee = []
                customerPriceFee = ([i[0] for i in customerPriceSQL])
            
                if outDateValid < today:
                    pass
                    
                else:
                    if advancedCancelDate >=60:
                        cancelMessage = "0"
                    if advancedCancelDate >=30 and advancedCancelDate <=59:
                        cancellationFee = customerPriceFee[0] / 2
                        cancelMessage = cancellationFee
                        toPay = True
                    if advancedCancelDate <=29:
                        cancellationFee = customerPriceFee[0]
                        cancelMessage = cancellationFee
                        toPay = True
                    session['cancelSession'] = [cancellationFee,userCancelationChoice[0],userCancelationChoice[1]]
                    session['reservationSession'] = reservationElement
                    return render_template('cancel.html',message=cancelMessage,pay = toPay,reservationInfo = session['reservationSession'],cancelSession = session['cancelSession'])

        #CHANGE USER PASSWORD
        userDetailsDB= []#gets data from the customer reservation
        cursor.execute("SELECT * FROM user WHERE idUser = (%s);",[userid],)
        userInformationSQL = cursor.fetchall()
        for row in userInformationSQL:
            tempUserRow= [row[1],row[2],row[3],row[4]]
            userDetailsDB.append(tempUserRow)

        error = None
        if "Update":
            if request.method == 'POST':
                passwordNew =  request.form['pass_new']
                passwordConfirm =  request.form['pass_confirm']
                passwordHashed = sha256_crypt.hash((str(passwordNew)))  
                if passwordNew:
                    if passwordNew == passwordConfirm :#adds new password to database
                        userRegisterData = cursor.execute("UPDATE user SET passwordHash = %s WHERE idUser = %s;",(passwordHashed,userid))
                        conn.commit()
                    else:
                        print(passwordNew)
                        redirect(url_for("homepage")) #refresh
                else:
                    error = "There is an error in your form"
                    redirect(url_for("homepage"))
        return render_template('userHomepage.html',email = session['email'], user = session['user'],userid = session['userid'],showAllBookings=reservationElement,message=cancelMessage,pay = toPay,error=error)
    else:
        redirect(url_for("login"))

@app.route('/cancel', methods=["GET","POST"])
@login_required
def cancel():
    if request.method == 'POST':
        conn = dbconn.getConnection()
        cursor = conn.cursor()
        cancelArray = session["cancelSession"]
        reservationArray = session["reservationSession"]
        if "cancelled":#cancelles the reservation
            deleteBookingCancellation = ("DELETE FROM customerreservation WHERE idReservation=%s;")
            cursor.execute(deleteBookingCancellation,(cancelArray[1],))
            conn.commit()

            addquantityCancellation = ("UPDATE hotel SET totalCapacity = totalCapacity+1 WHERE hotelCity = %s;") #adds rooms back to quanitity
            cursor.execute(addquantityCancellation,(cancelArray[2],))
            conn.commit() 

            if reservationArray[0][7] == "standard":
                addstandardCancellation = ("UPDATE hotel SET standardCapacity = standardCapacity+1 WHERE hotelCity = %s;")
                cursor.execute(addstandardCancellation,(cancelArray[2],))
                conn.commit() 
            if reservationArray[0][7] == "double":
                adddoubleCancellation = ("UPDATE hotel SET standardCapacity = standardCapacity+1 WHERE hotelCity = %s;")
                cursor.execute(adddoubleCancellation,(cancelArray[2],))
                conn.commit() 
            if reservationArray[0][7]== "family":
                addfamilyCancellation = ("UPDATE hotel SET standardCapacity = standardCapacity+1 WHERE hotelCity = %s;")
                cursor.execute(addfamilyCancellation,(cancelArray[2],))
                conn.commit() 
            reservationUpdateSQL = ("UPDATE cancelledreservation SET expired = 'yes' WHERE idReservation = %s;")    #updates the reservation to say that it is expired
            cursor.execute(reservationUpdateSQL,(reservationArray[0][0],))
            conn.commit() 
            reservationUpdateFeeSQL = ("UPDATE cancelledreservation SET cancelFee = %s WHERE idReservation = %s;")#update reservation to add cancellation fee
            cursor.execute(reservationUpdateFeeSQL,(cancelArray[0],reservationArray[0][0],))
            conn.commit() 
            return redirect(url_for('homepage'))
    
@app.route('/adminHomepage',methods=['GET','POST'])#admin homepage 
@login_required
def adminHomepage():
    if "admin" in session:
        admin = session["admin"]
        conn = dbconn.getConnection()
        cursor = conn.cursor() 
        error = None
        errorEditBool = False
        #SHOW ALL BOOKINGS
        cursor.execute("SELECT * FROM reservation LEFT JOIN guestInformation ON reservation.idReservation = guestInformation.idReservation UNION SELECT * FROM reservation RIGHT JOIN guestInformation ON reservation.idReservation = guestInformation.idReservation ")
        adminGetReservationSQL = cursor.fetchall()

        # #SHOWS HOTELS
        cursor.execute("SELECT * FROM hotel")
        hotelAll = cursor.fetchall()

        #CHANGE CAPACITY
        if request.method == 'POST':
            total_capacity = request.form['totalcap']
            standard_cap = request.form['standardcap']
            double_cap = request.form['doublecap']
            family_cap = request.form['familycap']
            specAddCapacity = int(standard_cap) + int(double_cap) + int(family_cap)  #validation for total capacity
            if int(specAddCapacity) != int(total_capacity):
                errorEditBool = True
                error = "Capacity doesn't match"
            if 'editCapacityRoom' in request.form: # if radio button pressed
                tempCapacityRoom = request.form['editCapacityRoom']
                radioCheckRoom = tempCapacityRoom.split()
            else:
                radioCheckRoom = ""
            if errorEditBool == False and radioCheckRoom != "":
                cursor.execute('UPDATE hotel SET totalCapacity = %s WHERE idHotel = %s;',(total_capacity,radioCheckRoom[0],)) 
                cursor.execute('UPDATE hotel SET standardCapacity = %s WHERE idHotel = %s;',(standard_cap,radioCheckRoom[0],))  
                cursor.execute('UPDATE hotel SET doubleCapacity = %s WHERE idHotel = %s;',(double_cap,radioCheckRoom[0],))  
                cursor.execute('UPDATE hotel SET familyCapacity = %s WHERE idHotel = %s;',(family_cap,radioCheckRoom[0],))  
                conn.commit()
                return redirect(url_for('adminHomepage'))
            else:
                error = "There is an error in your form"

        #SHOW CHARTS
        allDatesArray = []
        allDates = {}
        labels = ''
        data_months = ''
        for i in range(len(adminGetReservationSQL)):
            tempDates = adminGetReservationSQL[i][2]
            allDatesArray.append(tempDates.month)
        for monthDate in allDatesArray:
            tempDate = calendar.month_name[monthDate]
            allDates[tempDate] = allDates.get(tempDate, 0) + 1
        data_months = (list(allDates.values()))
        labels = (list(allDates.keys()))
        return render_template('adminHomepage.html',error=error,showAll = adminGetReservationSQL,hotels = hotelAll, labels=json.dumps(labels),data=json.dumps(data_months))
    else:
        return redirect(url_for('login'))

@app.route('/adminaddhotel', methods=["GET","POST"])
@login_required
def adminaddhotel():
    conn = dbconn.getConnection()
    cursor = conn.cursor()
    errorBool1 = False
    cursor.execute("SELECT * FROM hotel")
    adminHotelAll = cursor.fetchall()
    error = None
    try:
        if request.method == 'POST':
            idHotel = request.form['idHotel']
            city_hotel = request.form['city_hotel']
            total_capacity = request.form['total_capacity']
            off_peak = request.form['off_peak']
            on_peak = request.form['on_peak']
            standard_cap = request.form['standard_cap']
            double_cap = request.form['double_cap']
            family_cap = request.form['family_cap']
            addedCapacity = int(standard_cap) + int(double_cap) + int(family_cap)#validation for total capacity
            print(addedCapacity)
            print(total_capacity)
            if int(addedCapacity) != int(total_capacity):
                errorBool1 = True
            else:
                errorBool1 = False
            if errorBool1 == False:
                addNewHotel = cursor.execute("INSERT INTO hotel (idHotel,hotelCity,totalCapacity,offPeakPrice,onPeakPrice,standardCapacity,doubleCapacity,familyCapacity) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",(idHotel,city_hotel,total_capacity, off_peak,on_peak,standard_cap,double_cap,family_cap))
                conn.commit()
            else:
                error = "You have an error in your form, total capacity doesn't match"
    except mysql.connector.errors.IntegrityError:
        error = "You have an error in your form, Hotel ID already exists"
    cursor.close()
    conn.close()
    return render_template('addHotel.html',error=error,hotels = adminHotelAll)

@app.route('/logout')
def logout():
    session.pop('login',None)
    session.pop('email',None)
    session.pop('user',None)
    session.pop('admin',None)
    session.pop('reservationSession',None)
    return redirect(url_for('login'))

@app.route('/register',methods=['GET','POST']) 
def register():    
    conn = dbconn.getConnection()
    cursor = conn.cursor() 
    error = None
    form = RegisterForm(request.form)
    try:
        if request.method == 'POST' and form.validate():
            firstname = form.firstname.data
            lastname = form.lastname.data
            email = form.email.data
            password = form.password.data
            password = sha256_crypt.hash(password)  
            userRegisterData = cursor.execute("INSERT INTO user (firstName,lastName,email, passwordHash,userType) VALUES (%s,%s,%s,%s,'standard');",(firstname,lastname,email,password)) #adds form to database
            conn.commit()
            flash('You were successfully registered')
            cursor.close()
            conn.close()
            return redirect(url_for('login'))
    except mysql.connector.errors.IntegrityError: #checks if email is already in db
        error = 'Email address is taken'
        return render_template("Register.html",form=form,error=error) 
    cursor.close()
    conn.close()
    return render_template("Register.html",form=form) 

@app.route('/terms-and-conditions')
def TandC():
    return render_template('TandC.html')

@app.route('/privacy-policy')
def privpol():
    return render_template('privacypolicy.html')

@app.route('/search',methods=['GET','POST'])
@login_required
def search():
    conn = dbconn.getConnection()
    cursor = conn.cursor() 
    cursor.execute('SELECT idHotel,hotelCity FROM hotel')   #dynamic dropdown boxes
    city = cursor.fetchall() 
    error = None
    if request.method == 'POST': #gets data from form
        cityChoice = request.form['city'] 
        checkinChoice = request.form['indate']
        checkoutChoice = request.form['outdate']
        roomChoice = request.form['room']
        guestChoice = request.form['guestschecked']
        currencyChoice = request.form['currency']
        nightsTotal = datetime.strptime(checkoutChoice, '%Y-%m-%d') - datetime.strptime(checkinChoice, '%Y-%m-%d')
        conn = dbconn.getConnection()
        cursor = conn.cursor()
        if conn != None:
            cursor.execute('SELECT * FROM hotel WHERE idHotel = %s;', (cityChoice, ))   
            rows = cursor.fetchall()
            dbArray =[]
            validationArray = []
            for row in rows:#database and array validation
                dbArray.append(row[0])
                dbArray.append(row[1])
                dbArray.append(row[2])
                dbArray.append(row[3])
                dbArray.append(row[4])
                dbArray.append(row[5])
                dbArray.append(row[6])
                dbArray.append(row[7])

            #room validation
            if roomChoice == 'standard' and int(guestChoice) >= 2:
                validationArray.append('False')
            if roomChoice == 'double' and int(guestChoice) >= 3:
                validationArray.append('False')
            if roomChoice == 'family' and int(guestChoice) >= 7:
                validationArray.append('False')

            #date validation
            now= date.today()
            nowNew = str(now)
            newNow = time.strptime(nowNew,'%Y-%m-%d')
            newIn = time.strptime(checkinChoice, "%Y-%m-%d")
            newOut = time.strptime(checkoutChoice, "%Y-%m-%d")
            cursor.execute('SELECT checkOutDate FROM reservation;')     #gets rid of reservation if its passed the check out date
            datesExpired = cursor.fetchall()
            dateArray = []
            hotelDates = []
            hotelDatesCompare = []
            dateValidatedExpired = []
    
            dateToday = "{year}-{month}-{day}".format(year=newNow[0],month=newNow[1],day=newNow[2]) #todays date 
            todayDatesCompare = datetime.strptime(str(dateToday), "%Y-%m-%d")

            for row in datesExpired: #hotel date
                dateArray.append(row)
            hotelDates = ([i[0] for i in dateArray])
    
            for i in hotelDates:   #validates expired date to todays date
                temp = str(i)
                hotelDatesCompare= datetime.strptime(temp, "%Y-%m-%d")
                if hotelDatesCompare < todayDatesCompare:
                    dateValidatedExpired.append(i)

            for i in dateValidatedExpired: #gets the elements to check if they have already been made expired
                cursor.execute('SELECT expired FROM reservation WHERE checkOutDate = %s;',(i,))
                expiredCursor = cursor.fetchall()
                expiredRow = []
                for expiredCur in expiredCursor:
                    expiredCur = str(expiredCur).strip("(")
                    expiredCur = str(expiredCur).strip(")")
                    expiredCur = str(expiredCur).strip(",")
                    expiredCur = str(expiredCur).strip("'")	
                    expiredRow.append(expiredCur)
            
                cursor.execute('SELECT hotelInfo FROM reservation WHERE checkOutDate = %s AND expired != "yes";',(i,))
                dateAddCursor = cursor.fetchall()
                cursor.execute('SELECT roomType FROM reservation WHERE checkOutDate = %s AND expired != "yes";',(i,))
                roomAddCuror = cursor.fetchall()
                #adds quanitity back to hotel DB based on expired date
                if len(dateAddCursor) >= 1: #checks if database isnt empty
                    dateAddExpired = []
                    for addingCur in dateAddCursor:
                        addingCur = str(addingCur).strip("(")
                        addingCur = str(addingCur).strip(")")
                        addingCur = str(addingCur).strip(",")
                        addingCur = str(addingCur).strip("'")	
                        dateAddExpired.append(addingCur)
                    roomAddExpired = []
                    for roomCur in roomAddCuror:
                        roomCur = str(roomCur).strip("(")
                        roomCur = str(roomCur).strip(")")
                        roomCur = str(roomCur).strip(",")
                        roomCur = str(roomCur).strip("'")	
                        roomAddExpired.append(roomCur)
                    for element in dateAddExpired: #adds quantity back to total room
                        cursor.execute('UPDATE hotel SET totalCapacity = totalCapacity+1 WHERE idHotel = %s;',(element,))  
                        conn.commit() 
                        #makes the row expired so it isnt redone if function re-runs
                        cursor.execute('UPDATE reservation SET expired = "yes" WHERE hotelInfo = %s;',(element,))  
                        conn.commit() 
                        for i in range(len(roomAddExpired)): #adds quanitity back to each room
                            if  roomAddExpired[i] == "standard":
                                addstandard = ("UPDATE hotel SET standardCapacity = standardCapacity+1 WHERE idHotel = %s;")
                                cursor.execute(addstandard,(element,))
                                conn.commit() 
                            if roomAddExpired[i] == "double":
                                adddouble = ("UPDATE hotel SET doubleCapacity = standardCapacity+1 WHERE hotelCity = %s;")
                                cursor.execute(adddouble,(element,))
                                conn.commit() 
                            if roomAddExpired[i] == "family":
                                addfamily = ("UPDATE hotel SET familyCapacity = standardCapacity+1 WHERE hotelCity = %s;")
                                cursor.execute(addfamily,(element,))
                                conn.commit()
                else:
                    pass
            if newIn >= newOut:#for date form
                validationArray.append('False')
            elif newIn < newOut:
                dateValid = True
            else:
                validationArray.append('False')
            if newIn <= newNow or newOut <= newNow:
                validationArray.append('False')

            #peak or off peak
            checkInValidation = datetime.strptime(checkinChoice, '%Y-%m-%d')		
            if checkInValidation.month >= 4 and checkInValidation.month <= 9:
                cursor.execute('SELECT onPeakPrice FROM hotel WHERE idHotel = %s;', (cityChoice, ))   
                for i in cursor.fetchall() :
                    pricePerNight_standard = i[0]
            else:
                cursor.execute('SELECT offPeakPrice FROM hotel WHERE idHotel = %s;', (cityChoice, ))   
                for i in cursor.fetchall() :
                    pricePerNight_standard = i[0]

            #currency conversion
            if currencyChoice == 'eur':
                pricePerNight_standard = pricePerNight_standard * 1.2
            if currencyChoice == 'usdollars':
                pricePerNight_standard = pricePerNight_standard * 1.6

            #price multiplied by the number of nights
            nightsTotal = str(nightsTotal).split(" ")[0]
            nightsTotal = int(nightsTotal)
            pricePerNight_standard = pricePerNight_standard * nightsTotal
            
            #gets price of room
            if roomChoice == 'double' and int(guestChoice) == 1:
                percentagePrice = 20
            if roomChoice == 'double' and int(guestChoice) == 2:
                percentagePrice = 30
            if roomChoice == 'family':
                percentagePrice = 50
            if roomChoice == 'standard':
                percentagePrice = 0           
            totalPrice =  pricePerNight_standard * percentagePrice
            totalPrice = totalPrice / 100
            totalPrice = totalPrice + pricePerNight_standard

            #gets discount
            advancedDate = datetime.strptime(checkinChoice, '%Y-%m-%d') - datetime.strptime(nowNew, '%Y-%m-%d')	
            advancedDate = advancedDate.days
            if advancedDate >= 80 and advancedDate <= 90:
                advancedDiscount = 20
            if advancedDate >= 60 and advancedDate <= 79:
                advancedDiscount = 10
            if advancedDate >= 45 and advancedDate <= 59:
                advancedDiscount = 5
            if advancedDate <= 44:
                advancedDiscount = 0
            if advancedDate >= 91:
                validationArray.append('False')
                advancedDiscount = 0
            totalPriceDiscounted =  totalPrice * advancedDiscount
            totalPriceDiscounted = totalPriceDiscounted / 100
            totalPriceDiscounted =  totalPrice - totalPriceDiscounted

            cursor.execute('SELECT hotelCity FROM hotel WHERE idHotel = %s;', (cityChoice, ))   
            city_name = cursor.fetchall()
            cityNameArray = []
            for name in city_name:
                name = str(name).strip("(")
                name = str(name).strip(")")
                name = str(name).strip(",")
                name = str(name).strip("'")	
                cityNameArray.append(name)
            cityName = cityNameArray[0]
            
            if len(validationArray) >= 1:  #validation
                error = 'There is an error with your form'
            elif dbArray[2] == 0: #db validation for room quantity
                error = 'There are no more rooms available with your selection'
            elif dbArray[5] == 0 and roomChoice == 'standard':
                error = 'There are no more rooms available with your selection'
            elif dbArray[6] == 0 and roomChoice == 'double':
                error = 'There are no more rooms available with your selection'
            elif dbArray[7] == 0 and roomChoice == 'family':
                error = 'There are no more rooms available with your selection'
            else: #final validation before booking process begins
                if "email" in session and "user" in session :
                    email = session["email"] 
                    user = session["user"]
                    session['searchquery'] = [roomChoice,nightsTotal,totalPriceDiscounted,cityChoice,checkinChoice,checkoutChoice,guestChoice,cityName,newNow]
                    return redirect(url_for('hotel'))
                else:
                    return redirect(url_for("login")) 
            cursor.close()
            conn.close()
    return render_template("BookingPage.html",city=city,error=error) 

@app.route('/hotel/',methods=['GET','POST'])
@login_required
def hotel():
    searchquery = session.get('searchquery', None)
    email = session.get('email', None)
    if request.method == 'POST':
        if request.form['submit_book'] == 'book':
            conn = dbconn.getConnection()  #remove room from database
            cursor = conn.cursor()
            cursor.execute('SELECT totalCapacity,standardCapacity,doubleCapacity,familyCapacity FROM hotel WHERE hotelCity = %s;', (searchquery[7], ))  
            hotelMinusCapacity = cursor.fetchall()
            hotelMinusCapacity_new = []
            for minus in hotelMinusCapacity:
                hotelMinusCapacity_new.append(minus[0])
                hotelMinusCapacity_new.append(minus[1])
                hotelMinusCapacity_new.append(minus[2])
                hotelMinusCapacity_new.append(minus[3])	
            totalMinusCapacity = hotelMinusCapacity_new[0] - 1
            if searchquery[0] == 'standard':
                standardMinusCapacity = hotelMinusCapacity_new[1] - 1
                standardMinusCapacity_db=cursor.execute("UPDATE hotel set standardCapacity='%s' WHERE hotelCity = %s;",(standardMinusCapacity,searchquery[7]))
            if searchquery[0] == 'double':
                doubleMinusCapacity = hotelMinusCapacity_new[2] - 1
                doubleMinusCapacity_db=cursor.execute("UPDATE hotel set doubleCapacity='%s' WHERE hotelCity = %s;",(doubleMinusCapacity,searchquery[7]))
            if searchquery[0] == 'family':
                familyMinusCapacity = hotelMinusCapacity_new[3] - 1
                familyMinusCapacity_db=cursor.execute("UPDATE hotel set familyCapacity='%s' WHERE hotelCity = %s;",(familyMinusCapacity,searchquery[7]))
            hotelMinusCapacity_db=cursor.execute("UPDATE hotel set totalCapacity='%s' WHERE hotelCity = %s;",(totalMinusCapacity,searchquery[7]))
            conn.commit()
            date_today = searchquery[8]#adds data to reservation DB
            dateToday = "{year}-{month}-{day}".format(year=date_today[0],month=date_today[1],day=date_today[2])
            reservationDB = cursor.execute("INSERT INTO reservation (hotelInfo,checkInDate,checkOutDate,dateReserved) VALUES (%s,%s,%s,%s);",(searchquery[3],searchquery[4],searchquery[5],dateToday))
            conn.commit()
            idResNew = cursor.lastrowid
            guestreservationDB = cursor.execute("INSERT INTO guestinformation (idReservation,customerGuests,customerPrice,roomType) VALUES (%s,%s,%s,%s);",(idResNew,searchquery[6],searchquery[2],searchquery[0]))
            conn.commit()
            idGuestRes = cursor.lastrowid
            cancelledreservationB = cursor.execute("INSERT INTO cancelledreservation (idreservation,expired) VALUES (%s,%s);",(idResNew,"no"))
            conn.commit()

            cursor.execute('SELECT idUser,firstName,lastName,email FROM user WHERE email =%s ', (email, ))   #gets user details for booking receipt
            user_details = cursor.fetchall()
            userdetails = []
            for row in user_details:
                userdetails.append(row[0])
                userdetails.append(row[1])
                userdetails.append(row[2])
                userdetails.append(row[3])
       
            #adds userID and reservationID to database customerReservation
            cursor.execute('SELECT idReservation FROM reservation ORDER BY idReservation DESC LIMIT 1;')  
            cursor_reservation = cursor.fetchall()
            reservationID = []
            for row in cursor_reservation:
                reservationID.append(row[0])
            customerReservationSQL = cursor.execute("INSERT INTO customerreservation (idUserReservation,idReservation) VALUES (%s,%s);",(userdetails[0],reservationID[0]))
            conn.commit()
            cursor.close()
            conn.close()
            return render_template("Book.html",searchQuery=searchquery,userDetails=userdetails,bookingID=reservationID[0])
    return render_template("BookingProcess.html",searchQuery=searchquery)

if __name__ == '__main__':
    app.run(debug = True)


