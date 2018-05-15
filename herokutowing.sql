= = = = = = = = = = = = = = = = = =

CREATE TABLE operators (
    operatorid SERIAL PRIMARY KEY,
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    email VARCHAR(50) UNIQUE,
    hash VARCHAR(255),
    cell VARCHAR(10),
    member INTEGER,
    date_registered VARCHAR(50),
    companyid VARCHAR(9) REFERENCES companies(companyid)
);


= = = = = = = = = = = = = = = = = =

CREATE TABLE owners (
    ownerid SERIAL PRIMARY KEY,
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    email VARCHAR(50) UNIQUE,
    hash VARCHAR(255),
    cell VARCHAR(10),
    date_registered VARCHAR(50)
);


= = = = = = = = = = = = = = = = = =

CREATE TABLE companies (
    companyid VARCHAR(9) PRIMARY KEY,
    companyname VARCHAR(50),
    phone VARCHAR(10)
);


= = = = = = = = = = = = = = = = = =

CREATE TABLE trucks (
    truckid SERIAL PRIMARY KEY,
    make VARCHAR(50),
    model VARCHAR(50),
    licenseplate VARCHAR(50),
    companyid VARCHAR(9) REFERENCES companies(companyid),
    operatorid INTEGER REFERENCES operators(operatorid)
);


= = = = = = = = = = = = = = = = = =

CREATE TABLE owners_companies (
    ownerid INTEGER REFERENCES owners(ownerid),
    companyid VARCHAR(9) REFERENCES companies(companyid)
);


= = = = = = = = = = = = = = = = = =

CREATE TABLE pounds (
    poundid SERIAL PRIMARY KEY,
    address VARCHAR(100),
    city VARCHAR(50),
    phone VARCHAR(10),
    companyid VARCHAR(9) REFERENCES companies(companyid)
);


= = = = = = = = = = = = = = = = = =

CREATE TABLE archived_operators (
    date_archived VARCHAR(50),
    date_registered VARCHAR(50),
    operatorid INTEGER REFERENCES operators(operatorid),
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    email VARCHAR(50),
    hash VARCHAR(255),
    cell VARCHAR(10),
    companyid VARCHAR(9) REFERENCES companies(companyid)
);


= = = = = = = = = = = = = = = = = =

CREATE TABLE archived_trucks (
    truckid INTEGER,
    make VARCHAR(50),
    model VARCHAR(50),
    licenseplate VARCHAR(50),
    companyid VARCHAR(9) REFERENCES companies(companyid),
    operatorid INTEGER REFERENCES operators(operatorid)
);


= = = = = = = = = = = = = = = = = =

CREATE TABLE archived_pounds (
    poundid integer,
    address VARCHAR(100),
    city VARCHAR(50),
    phone VARCHAR(10),
    companyid VARCHAR(9) REFERENCES companies(companyid)
);


= = = = = = = = = = = = = = = = = =

CREATE TABLE customers (
    customerid SERIAL PRIMARY KEY,
    name VARCHAR(50),
    address VARCHAR(100),
    phone VARCHAR(10),
    insurancecompany VARCHAR(50),
    insurancepolicy VARCHAR(50)
);


= = = = = = = = = = = = = = = = = =

CREATE TABLE cust_vehicles (
    vehicleid SERIAL PRIMARY KEY,
    year VARCHAR(4),
    make VARCHAR(50),
    model VARCHAR(50),
    mileage VARCHAR(10),
    color VARCHAR(10),
    licenseplate VARCHAR(50),
    vin VARCHAR(25),
    customerid INTEGER REFERENCES customers(customerid),
    operatorid INTEGER REFERENCES operators(operatorid)
);


= = = = = = = = = = = = = = = = = =

CREATE TABLE incidents (
    incidentid SERIAL PRIMARY KEY,
    incidentdate VARCHAR(50),
    lat VARCHAR(50),
    lng VARCHAR(50),
    dropofflat VARCHAR(50),
    dropofflng VARCHAR(50),
    crcused VARCHAR(50),
    flattire INTEGER,
    flatbed INTEGER,
    dollies INTEGER,
    boost INTEGER,
    fuel INTEGER,
    winch INTEGER,
    lockout INTEGER,
    collision INTEGER,
    towed INTEGER,
    keys INTEGER,
    companyid VARCHAR(9) REFERENCES companies(companyid),
    operatorid INTEGER REFERENCES operators(operatorid),
    vehicleid INTEGER REFERENCES cust_vehicles(vehicleid),
    poundid INTEGER REFERENCES pounds(poundid)
);


= = = = = = = = = = = = = = = = = =

CREATE TABLE impounded_vehicles (
    status INTEGER DEFAULT 1,
    impounded_date VARCHAR(50),
    pickup VARCHAR(50),
    vehicleid INTEGER REFERENCES cust_vehicles(vehicleid),
    poundid INTEGER REFERENCES pounds(poundid),
    operatorid INTEGER REFERENCES operators(operatorid)
);


= = = = = = = = = = = = = = = = = =

CREATE TABLE active_trucks (
    lat VARCHAR(25),
    lng VARCHAR(25),
    operatorid INTEGER UNIQUE REFERENCES operators(operatorid)
);


= = = = = = = = = = = = = = = = = =

#TODO: timestamp on each coordinate update

CREATE TABLE active_users (
    usertype VARCHAR(10),
    userid INTEGER UNIQUE REFERENCES operators(operatorid),
    companyid VARCHAR(9) REFERENCES companies(companyid)
);
