from flask import Flask, flash, redirect, render_template, request, session, jsonify, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from decimal import Decimal
from helpers import apology, login_required

import sys
import psycopg2
import datetime

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SECRET_KEY"] = "b'L\xc7\x9b\xaf:T\x01\xc6;\xbb\xa8W\x8d\xc6A}"

sess = Session()
sess.init_app(app)

if __name__ == '__main__':
    app.run(debug = True)
    print("__name__ == __main__")

# Configure PostgreSQL database
connectinfo = 'dbname=d4hkq813fgmja7 host=ec2-54-83-1-94.compute-1.amazonaws.com port=5432 user=jrpsctanoouwyp password=9a83ff80fe7f40f5b3337a4f87ede28ab03bca64f300ac26b3f7f6a6637d026d sslmode=require'

try:
    conn = psycopg2.connect(connectinfo)
    print("[debug:loaded]")
    print("Connected to database")
    db = conn.cursor()

except:
    print("[debug:loaded]")
    print("Unable to connect database")

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/getUserId")
def getUserId():
    """Send user id to client-side"""

    userid = str(session['userid'])
    
    return userid



@app.route("/getCompanyName", methods=["GET","POST"])
def getCompanyName():
    """return company name from code"""

    companyname = ""
    if request.method == "POST":

        # check/store company code
        if not request.form.get("companyid"):
            return apology("must provide company code", 403)
        companyid = request.form.get("companyid") 

        # query database for company code
        db.execute("""SELECT companyname FROM companies 
                      WHERE companyid = %s;""", (companyid,))
        
        rows = db.fetchall()
        if len(rows) > 0:
            companyname = rows[0]

    return companyname


@app.route("/requestOwnership", methods=["GET", "POST"])
def requestOwnership():
    """Request being added as company owner"""

    if request.method == "POST":
        
        # check/store company id
        if not request.form.get("companyid"):
            return apology("Missing company id.")
        companyid = request.form.get("companyid")

        # check/store owner name
        if not request.form.get("firstname"):
            return apology("Missing first name.")
        if not request.form.get("lastname"):
            return apology("Missing last name.")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        
        # check/store owner email
        if not request.form.get("email"):
            return apology("Missing email address.")
        email = request.form.get("email")

        # check/store owner password
        if not request.form.get("password"):
            return apology("Enter a password.")
        elif not request.form.get("confirmation"):
            return apology("Confirm password.")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match.")
        hash = generate_password_hash(request.form.get("password"))

        # check/store owner cell
        if not request.form.get("cell"):
            return apology("Missing cell address.")
        cell = request.form.get("cell")

        # insert new owner into database
        result = db.execute("""INSERT INTO owners (firstname, lastname, 
                               email, hash, cell) VALUES (%s,%s,%s,%s,%s);""",
                               (firstname, lastname, email, hash, cell))

        # user must provide unique email address 
        if not result:
            return apology("Email address already in use.")

        # query for current owner
        db.execute("""SELECT owners.ownerid FROM owners INNER JOIN owners_companies 
                      ON owners_companies.ownerid = owners.ownerid WHERE 
                      owners_companies.companyid = %s;""", (companyid, ))

        rows = db.fetchall() 
        ownerid = rows[0][0]
        # TODO: send request to current owner with new ownerid

        conn.commit()

        # successful registration direct
        return render_template("login.html")

    # request ownership redirect
    else:
        return render_template("requestownership.html")

@app.route("/registerCompany", methods=["GET", "POST"])
def registerCompany():
    """Register company"""

    if request.method == "POST":

        companyid = request.form.get("companyid")
        companyname = request.form.get("companyname")
        phone = request.form.get("phone")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")

        # check/store owner password
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match.")
        hash = generate_password_hash(request.form.get("password"))
        
        # query database for company
        db.execute("""SELECT companyname 
                        FROM companies
                       WHERE companyname = %s;""", (companyname,))

        rows = db.fetchall()
        if len(rows) > 0:
            return apology("Company name exists. Re-enter correct incorporation number.")

        # insert new owner into database
        db.execute("""INSERT INTO owners (
                            firstname, 
                            lastname, 
                            email, 
                            hash, 
                            date_registered ) 
                       VALUES (%s,%s,%s,%s,CURRENT_TIMESTAMP);""", 
                       (firstname, lastname, email, hash))

        # insert new company into database
        db.execute("""INSERT INTO companies (
                        companyid, 
                        companyname, 
                        phone ) 
                      VALUES (%s,%s,%s);""", 
                      (companyid, companyname, phone))
        conn.commit()

        # get newly registered owner id
        db.execute("""SELECT ownerid FROM owners WHERE email = %s;""", (email, ))
        rows = db.fetchall()
        ownerid = rows[0][0]

        # call link function
        linkOwnerCompany(ownerid, companyid)
        
        print("[debug:registerCompany]")
        print("Registered: " + companyname + " (" + companyid + ")")
        print("Owner: " + firstname + " " + lastname)


        # successful registration redirect
        return render_template("login.html")

    # registration redirect
    else:
        return render_template("registercompany.html")


@app.route("/registerOperator", methods=["GET", "POST"])
def registerOperator():
    """Register operator"""

    if request.method == "POST":

        # check for name
        if not request.form.get("firstname"):
            return apology("Missing first name.")
        if not request.form.get("lastname"):
            return apology("Missing last name.")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")

        # check for email
        if not request.form.get("email"):
            return apology("Missing email address.")
        email = request.form.get("email")

        # check/store owner password
        if not request.form.get("password"):
            return apology("Enter a password.")
        elif not request.form.get("confirmation"):
            return apology("Confirm password.")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match.")
        hash = generate_password_hash(request.form.get("password"))

        # check for company id
        if not request.form.get("companyid"):
            return apology("Missing company id")
        companyid = request.form.get("companyid")

        # insert new user into database
        db.execute("""INSERT INTO operators (
                        firstname, 
                        lastname, 
                        email, 
                        hash, 
                        member, 
                        date_registered, 
                        companyid ) 
                      VALUES (%s,%s,%s,%s,%s,CURRENT_TIMESTAMP,%s);""",
                      (firstname, lastname, email, hash, 0, companyid))

        conn.commit()

        print("\n")
        print("[debug:registerOperator]")
        print("Registering: " + email + " ...")
        print("First name: " + firstname)
        print("Last name: " + lastname)
        print("Company ID: " + companyid)

        # successful registration redirect
        return render_template("login.html")


    # registration redirect
    else:
        return render_template("registeroperator.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    userid = None
    usertype = ""
    companyid = ""

    # user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Form submission check 
        email = request.form.get("email")
        usertype = request.form.get("usertype")

        rows = None
        
        # query database for email address
        if usertype == "Operator":
            db.execute("""SELECT operatorid, email, hash 
                            FROM operators
                           WHERE email = %s;""", (email,))
            rows = db.fetchall()

        elif usertype == "Owner":
            db.execute("""SELECT ownerid, email, hash 
                            FROM owners 
                           WHERE email = %s;""", (email,))
            rows = db.fetchall()

        # ensure username exists and password is correct
        if len(rows) !=1:
            return apology("Email not recognized", 403)
        elif not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("Incorrect password", 403)

        # remember which user has logged in
        userid = rows[0][0]
        
        if usertype == "Owner":
            # store companyid
            db.execute("""SELECT companyid 
                            FROM owners_companies 
                           WHERE ownerid=%s;""", (userid, ))
            rows = db.fetchall() 
            companyid = rows[0][0]

        elif usertype == "Operator":
            # store companyid
            db.execute("""SELECT companyid 
                            FROM operators 
                           WHERE operatorid=%s;""", (userid, ))
            rows = db.fetchall() 
            companyid = rows[0][0] 

        print("[debug:login]")
        print("Logging in: " + email)
        print("User ID: " + str(userid))
        print("User Type: " + usertype)
        print("Company ID: " + companyid)

        if usertype == "Operator":
            # insert new active operator into table
            db.execute("""INSERT INTO active_users (
                            usertype,
                            userid,
                            companyid
                          ) VALUES (
                            %s,
                            %s,
                            %s 
                          ) ON CONFLICT (userid)
                          DO UPDATE
                          SET usertype = excluded.usertype,
                              companyid = excluded.companyid;""", \
                                      (usertype,userid,companyid,))
            conn.commit()

        session['userid'] = userid
        if 'userid' in session:
            session['usertype'] = usertype
            session['companyid'] = companyid
        else:
            print("session not available")

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/")
@login_required
def index():
    """Logged in screen"""

    # display relevant dashboard (owner/operator)
    if session["usertype"] == "Owner":
        return redirect("/teamManagement")

    elif session["usertype"] == "Operator":
        # consider: return render_template to remember session
        return redirect("/map")


@app.route("/searchCompany")
def searchCompany():
    """Search for companies that match query"""
    # TODO: NOT WORKING

    # check for query
    if not request.args.get("q"):
        raise RuntimeError("Search failed")

    # add wildcard to query and search database
    q = request.args.get("q") + "%"
    #q = "%" + request.args.get("q") + "%"
    db.execute("""SELECT * FROM companies WHERE companyid LIKE %s 
                  OR companyname LIKE %s LIMIT 5;""", (q,q))
    
    rows = db.fetchall()
    
    return jsonify(rows)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    """Change user password"""
    
    oldhash = None
    rows = None

    if request.method =="POST":
        # ensure form completion
        if not request.form.get("oldpassword"):
            return apology("Enter old password")
        elif not request.form.get("newpassword"):
            return apology("Enter new password")
        elif not request.form.get("confirmation"):
            return apology("Confirm new password")

        # check for matching new password
        elif request.form.get("newpassword") != request.form.get("confirmation"):
            return apology("New passwords do not match")

        # query for hash of password
        if session["usertype"] == "Owner":
            db.execute("""SELECT hash 
                            FROM owners 
                           WHERE ownerid = %s;""", \
                          (session["userid"],))
            rows = db.fetchall()
        elif session["usertype"] == "Operator":
            db.execute("""SELECT hash 
                            FROM operators 
                           WHERE operatorid = %s;""", \
                          (session["userid"],))
            rows = db.fetchall()

        oldhash = rows[0][0]

        # check current password validity
        if not check_password_hash(oldhash, request.form.get("oldpassword")):
            return apology("Re-enter current password")

        # check for the use
        # hash and update new password
        if session["usertype"] == "Owner":
            db.execute("""UPDATE owners 
                            SET hash = %s 
                            WHERE ownerid = %s""", \
                            (generate_password_hash(request.form.get("newpassword")), 
                            session["userid"]))

        elif session["usertype"] == "Operator":
            db.execute("""UPDATE operators 
                            SET hash = %s 
                            WHERE operatorid = %s""", \
                            (generate_password_hash(request.form.get("newpassword")), 
                            session["userid"]))

        # save changes to the database
        conn.commit()

        # password change success, send home
        return redirect("/")

    else:
        # password change failed, refresh settings
        return render_template("settings.html")



####################################################################
########################## Owner Functions #########################
####################################################################

@app.route("/teamManagement")
@login_required
def teamManagement():
    """Owner team management page"""
    
    # query for operators in company
    db.execute("""SELECT * FROM operators 
                    WHERE companyid=%s""", 
            (session["companyid"], ))
    team = db.fetchall()

    # pass team to jinja in html
    return render_template("teammanagement.html", team=team)

    

@app.route("/removeOperator", methods=["GET", "POST"])
def removeOperator():
    """Owner removes operator from team"""

    if not request.args.get("operatorid"):
        raise RuntimeError("Error: something went wrong!")

    operatorid = request.args.get("operatorid")

    # query for operator details
    db.execute("""SELECT 
                    date_registered,
                    operatorid,
                    firstname,
                    lastname,
                    email,
                    hash,
                    cell,
                    companyid 
                  FROM operators
                  WHERE operatorid=%s;""", (operatorid, ))
    operator = db.fetchall()[0]

    # add operator into archived_operators table
    db.execute("""INSERT INTO archived_operators (
                    date_archived,
                    date_registered,
                    operatorid,
                    firstname,
                    lastname,
                    email,
                    hash,
                    cell,
                    companyid )
                  VALUES (CURRENT_TIMESTAMP,%s,%s,%s,%s,%s,%s,%s,%s);""", (
                    operator[0],
                    operator[1],
                    operator[2],
                    operator[3],
                    operator[4],
                    operator[5],
                    operator[6],
                    operator[7], ))
    conn.commit()
        
    # delete operator from operators
    db.execute("""DELETE FROM operators
                  WHERE operatorid = %s;""", 
                  (operatorid, )) 
    conn.commit()

    # reload team management page
    return teamManagement() 



@app.route("/truckManagement")
@login_required
def truckManagement():
    """Owner truck management page"""

    companyid = session["companyid"] 

    # query for company trucks
    db.execute("""SELECT * FROM trucks WHERE companyid=%s""", 
                  (companyid, ))
    garage = db.fetchall()

    # pass garage to jinja in html
    return render_template("truckmanagement.html", garage=garage)



@app.route("/addTruck", methods=["GET", "POST"])
@login_required
def addTruck():
    """Add truck to company fleet"""

    if request.method == "POST":

        # check/store truck make
        if not request.form.get("make"):
            return apology("Missing make.")
        make = request.form.get("make")

        # check/store truck model
        if not request.form.get("model"):
            return apology("Missing model.")
        model = request.form.get("model")

        # check/store truck license plate
        if not request.form.get("licenseplate"):
            return apology("Missing license plate number.")
        licenseplate = request.form.get("licenseplate")
        
        companyid = session["companyid"]

    #TODO: assign operator to truck (currently nullable in db)
        #operatorid = session["operatorid"]
        
        db.execute("""INSERT INTO trucks (
                        make, 
                        model, 
                        licenseplate, 
                        companyid )
                      VALUES (%s,%s,%s,%s);""", (
                        make, 
                        model, 
                        licenseplate, 
                        companyid, ))
        conn.commit()

        # redirect user to pound management
        return redirect("/truckManagement")

    else:
        # redirect to form
        return render_template("addtruck.html")




@app.route("/removeTruck", methods=["GET", "POST"])
def removeTruck():
    """Owner removes truck from company"""

    if not request.args.get("truckid"):
        raise RuntimeError("Error: something went wrong!")

    truckid = request.args.get("truckid")

    # query for operator details
    db.execute("""SELECT 
                    truckid,
                    make,
                    model,
                    licenseplate,
                    companyid,
                    operatorid
                  FROM trucks
                  WHERE truckid=%s;""", (truckid, ))
    truck = db.fetchall()[0]

    # add operator into archived_trucks table
    db.execute("""INSERT INTO archived_trucks (
                    truckid,
                    make,
                    model,
                    licenseplate,
                    companyid,
                    operatorid )
                  VALUES (%s,%s,%s,%s,%s,%s);""", (
                    truck[0],
                    truck[1],
                    truck[2],
                    truck[3],
                    truck[4],
                    truck[5], ))
    conn.commit()
        
    # delete operator from operators
    db.execute("""DELETE FROM trucks
                  WHERE truckid = %s;""", (truckid, )) 
    conn.commit()

    # reload team management page
    return truckManagement() 



@app.route("/poundManagement")
@login_required
def poundManagement():
    """Owner team management page"""
    # display pound information

    companyid = session["companyid"] 

    # query for pounds
    db.execute("""SELECT * FROM pounds WHERE companyid=%s""", 
                  (companyid, ))
    pounds = db.fetchall()

    # pass pounds to jinja in html
    return render_template("poundmanagement.html", pounds=pounds)



@app.route("/addPound", methods=["GET", "POST"])
@login_required
def addPound():
    """Add new pound to company"""

    if request.method == "POST":

        # check/store pound address
        if not request.form.get("address"):
            return apology("Missing address.")
        address = request.form.get("address")

        # check/store pound city
        if not request.form.get("city"):
            return apology("Missing city.")
        city = request.form.get("city")

        # check/store pound phone number
        if not request.form.get("phone"):
            return apology("Missing company phone number.")
        phone = request.form.get("phone")
        
        companyid = session["companyid"]

    #TODO: Geocode address and store long, lat%s or consider calling function to retrieve geocode%s

        db.execute("""INSERT INTO pounds (
                        address, 
                        city, 
                        phone, 
                        companyid )
                      VALUES (%s,%s,%s,%s);""", (
                        address, 
                        city, 
                        phone, 
                        companyid, ))
        conn.commit()

        # redirect user to pound management
        return redirect("/poundManagement")

    else:
        # redirect to form
        return render_template("addpound.html")



@app.route("/removePound", methods=["GET", "POST"])
def removePound():
    """Owner removes pound from company"""

    if not request.args.get("poundid"):
        raise RuntimeError("Error: something went wrong!")

    poundid = request.args.get("poundid")

    # query for operator details
    db.execute("""SELECT 
                    poundid,
                    address,
                    city,
                    phone,
                    companyid
                  FROM pounds
                  WHERE poundid=%s;""", (poundid, ))
    pound = db.fetchall()[0]

    archived_date = datetime.datetime.now()

    # add pound into archived_pounds table
    db.execute("""INSERT INTO archived_pounds (
                    poundid,
                    address,
                    city,
                    phone,
                    companyid )
                  VALUES (%s,%s,%s,%s,%s);""", (
                    pound[0],
                    pound[1],
                    pound[2],
                    pound[3],
                    pound[4], ))
    conn.commit()
        
    # delete operator from operators
    db.execute("""DELETE FROM pounds
                  WHERE poundid = %s;""", 
                  (poundid, )) 
    conn.commit()

    # reload pound management page
    return poundManagement() 




####################################################################
######################## Operator Functions ########################
####################################################################

@app.route("/incidentReportForm", methods=["GET", "POST"])
@login_required
def incidentReportForm():
    """Incident Report Form"""
    # submission of incident report

    if request.method =="POST":

        # check/store customer information
        if not request.form.get("name"):
            return apology("Enter customer name")
        elif not request.form.get("address"):
            return apology("Enter customer address")
        elif not request.form.get("phone"):
            return apology("Enter customer phone number")
        elif not request.form.get("insurancecompany"):
            return apology("Enter customer insurance company")
        elif not request.form.get("insurancepolicy"):
            return apology("Enter customer insurance policy number")

        # input from customer information
        name = request.form.get("name")
        address = request.form.get("address")
        phone = request.form.get("phone")
        insurancecompany = request.form.get("insurancecompany")
        insurancepolicy = request.form.get("insurancepolicy")

        # add to table: customers
        db.execute("""INSERT INTO customers (
                        name,
                        address,
                        phone,
                        insurancecompany,
                        insurancepolicy )
                      VALUES (%s,%s,%s,%s,%s);""", (
                        name,
                        address,
                        phone,
                        insurancecompany,
                        insurancepolicy, ))

        # check/store customer vehicle details
        if not request.form.get("year"):
            return apology("Enter vehicle year")
        elif not request.form.get("make"):
            return apology("Enter vehicle make")
        elif not request.form.get("model"):
            return apology("Enter vehicle model")
        elif not request.form.get("mileage"):
            return apology("Enter vehicle mileage")
        elif not request.form.get("color"):
            return apology("Enter vehicle color")
        elif not request.form.get("licenseplate"):
            return apology("Enter vehicle license plate")
        elif not request.form.get("vin"):
            return apology("Enter vehicle VIN") 
        
        # input from customer vehicle details
        year = request.form.get("year")
        make = request.form.get("make")
        model = request.form.get("model")
        mileage = request.form.get("mileage")
        color = request.form.get("color")
        licenseplate = request.form.get("licenseplate")
        vin = request.form.get("vin")
        operatorid = session["userid"]

        # add to table: cust_vehicles
        db.execute("""INSERT INTO cust_vehicles (
                        year,
                        make,
                        model,
                        mileage,
                        color,
                        licenseplate,
                        vin,
                        operatorid )
                      VALUES (%s,%s,%s,%s,%s,%s,%s,%s);""", (
                        year,
                        make,
                        model,
                        mileage,
                        color,
                        licenseplate,
                        vin,
                        operatorid, ))

        # check/store incident details
        if not request.form.get("pickup"):
            return apology("Enter incident location")
        elif not request.form.get("dropoff"):
            return apology("Enter drop-off location")
        #elif not request.form.get("crcused"):
        #    return apology("TODO: DEAL WITH NO CRC")
        
        # input from incident details
        pickup = request.form.get("pickup")
        dropoff = request.form.get("dropoff")
        crcused = request.form.get("crcused")
        flattire = request.form.get("flattire")
        flatbed = request.form.get("flatbed")
        dollies = request.form.get("dollies")
        boost = request.form.get("boost")
        fuel = request.form.get("fuel")
        winch = request.form.get("winch")
        lockout = request.form.get("lockout")
        collision = request.form.get("collision")
        towed = request.form.get("towed")
        keys = request.form.get("keys")
        poundid = request.form.get("poundid")
        companyid = session["companyid"] 

        db.execute("""SELECT vehicleid 
                        FROM cust_vehicles
                       WHERE vin=%s;""", (vin, ))
        vehicleid = db.fetchall()[0][0]

        # add to table: incidents
        db.execute("""INSERT INTO incidents (
                        incidentdate,
                        pickup,
                        dropoff,
                        crcused,
                        flattire,
                        flatbed,
                        dollies,
                        boost,
                        fuel,
                        winch,
                        lockout,
                        collision,
                        towed,
                        keys,
                        companyid,
                        operatorid,
                        vehicleid,
                        poundid )
                      VALUES (CURRENT_TIMESTAMP,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""", (
                        pickup,
                        dropoff,
                        crcused,
                        flattire,
                        flatbed,
                        dollies,
                        boost,
                        fuel,
                        winch,
                        lockout,
                        collision,
                        towed,
                        keys,
                        companyid,
                        operatorid,
                        vehicleid,
                        poundid, ))

        # add to table: impounded_vehicles
        db.execute("""INSERT INTO impounded_vehicles (
                        impounded_date,
                        vehicleid,
                        poundid,
                        operatorid )
                      VALUES (CURRENT_TIMESTAMP,%s,%s,%s);""", (
                        vehicleid,
                        poundid,
                        operatorid, ))
        conn.commit()

        return redirect("/incidentHistory")

    return render_template("incidentreport.html")

@app.route("/incidentHistory")
@login_required
def incidentHistory():
    """Operator incident history"""
    operatorid = session["userid"] 

    # query for company trucks
    db.execute("""SELECT * FROM incidents WHERE operatorid=%s""", 
                  (operatorid, ))
    history = db.fetchall()

    # pass list of incidents to jinja in html
    return render_template("incidenthistory.html", history=history)


@app.route("/impoundedVehicles")
#@login_required
def impoundedVehicles():
    """Operator's list of impounded vehicles"""
    operatorid = session['userid']
    
    db.execute("""SELECT 
                    status, 
                    poundid, 
                    impounded_date,
                    cust_vehicles.year, 
                    cust_vehicles.make, 
                    cust_vehicles.model 
                  FROM impounded_vehicles 
                  INNER JOIN cust_vehicles 
                  ON cust_vehicles.vehicleid = impounded_vehicles.vehicleid 
                  WHERE cust_vehicles.operatorid = %s;""", 
                  (operatorid, ))

    # query for impounded vehicles by operatorid
    impounded_vehicles = db.fetchall()
    print(impounded_vehicles)

    # pass list of incidents to jinja in html
    return render_template("impoundedvehicles.html", impounded_vehicles=impounded_vehicles)



##############################################################
######################## Map Function ########################
##############################################################

@app.route("/map")
@login_required
def map():
    """Owner team management page"""
    # display relevant dashboard (owner/operator)

    return render_template("map.html")



@app.route("/updateCoordinates")
def updateCoordinates():
    """Update truck coordinates in database"""

    activetrucks = []
    lat = request.args.get("lat")
    lng = request.args.get("lng")

    if 'userid' in session and session["usertype"] == "Operator":
        print("[debug:updateCoords]")
        print("Operator ID: " + str(session['userid']))
        print("Latitude: " + lat)
        print("Longitude: " + lng)

        # for testing purposes, we'll record all position changes
        db.execute("""INSERT INTO active_trucks (
                        lat, 
                        lng, 
                        operatorid 
                      ) VALUES (
                        %s,
                        %s,
                        %s 
                      ) ON CONFLICT (operatorid)
                      DO UPDATE
                      SET lat = excluded.lat,
                          lng = excluded.lng;""", \
                      (lat,lng,session["userid"],))
        conn.commit()
    else:
        print("[debug:updateCoords]")
        print("Error updating active_trucks with new coordinates.")

    db.execute("""SELECT * FROM active_trucks;""")
    activetrucks = db.fetchall()

        
    return jsonify(activetrucks)



@app.route("/update")
def update():
    """get active truck coordinates"""
    
    trucks = []

    # get position of active trucks
    db.execute("""SELECT operatorid, lat, lon 
                    FROM active_trucks 
                    WHERE operatorid = %s;""", \
                    (session["userid"],))

    rows = db.fetchall()

    for row in rows:

        truck = {
                "operatorid": row[0],
                "lat": row[1],
                "lon": row[2]
        }
        
        trucks.append(truck.copy())

    return trucks



@app.route("/createIncidentReport")
def createIncidentReport():
    """Insert incident report coordinates into database"""

    lat = request.args.get("lat")
    lng = request.args.get("lng")
    incidentid = None

    # TODO: this fails randomly, due to lack of session maybe?
    if 'userid' in session:

        db.execute("""INSERT INTO incidents (
                        incidentdate,
                        lat,
                        lng,
                        operatorid
                    ) VALUES ( 
                        CURRENT_TIMESTAMP,
                        %s,
                        %s,
                        %s 
                    ) RETURNING incidentid;""", \
                    (lat,lng,session["userid"],))
        conn.commit()

        incidentid = db.fetchall()[0][0]

        print("[debug:createIncidentReport] Operator created new incident..")
        print("User ID: " + str(session['userid']))
        print("Incident ID: " + str(incidentid))
        print("Latitude: " + str(lat))
        print("Longitude: " + str(lng))

        return str(incidentid)

    else:
        print("[debug:createIncidentReport]")
        print("Error creating new incident report.")
        return "False"


@app.route("/updateIncidentReport")
def updateIncidentReport():
    """Update incident report coordinates in database"""
    
    incidentid = request.args.get('incidentid')
    lat = request.args.get('lat')
    lng = request.args.get('lng')

    db.execute("""UPDATE incidents 
                    SET lat = %s,
                        lng = %s
                    WHERE incidentid = %s""", \
                    (lat, lng, incidentid))
    conn.commit()

    print("[debug:updateIncidentReport] Operator dragged incident marker..")
    print("User ID: " + str(session['userid']))
    print("Incident ID: " + str(incidentid))
    print("Updated latitude: " + str(lat))
    print("Updated longitude: " + str(lng))

    return "True"



@app.route("/logout")
def logout():
    """Log user out"""

    if 'userid' in session:
        db.execute("""DELETE FROM active_users
                      WHERE userid = %s;""", 
                      (session['userid'], )) 
        db.execute("""DELETE FROM active_trucks
                      WHERE operatorid = %s;""", 
                      (session['userid'], )) 
        conn.commit()

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

        

def linkOwnerCompany(ownerid, companyid):
    """Create link between company and owner in owners_companies"""
    
    # add link in joint table for owner & company
    db.execute("""INSERT INTO owners_companies 
                      VALUES (%s, %s);""", 
                      (ownerid, companyid))
    
    conn.commit()
    

def errorhandler(e):
    """Handle error"""

    #if usertype != None:
    #    db.execute("""DELETE FROM active_users
    #                  WHERE userid = %s;""", 
    #                  (userid, )) 
    #    conn.commit()

    return apology(e.name, e.code)



# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
