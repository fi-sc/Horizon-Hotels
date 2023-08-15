-- Name of programmer: Fiorella Scarpino 
-- Student ID: 21010043
-- Date: 1/05/2022
-- Final Version. Created with SQL
-- Description of program: Database dumps


--create the database
--CREATE DATABASE horizonhotelDB;

USE horizonhotelDB;



--creates user table
CREATE TABLE user 
(
    idUser int AUTO_INCREMENT NOT NULL,
    firstName varchar(45)NOT NULL,
    lastName varchar(45)NOT NULL,
    email varchar(100) UNIQUE NOT NULL,
    passwordHash VARCHAR(128),
    userType char(8)NOT NULL DEFAULT 'standard',
    PRIMARY KEY (idUser)
);


--creates hotel table
CREATE TABLE hotel 
(
    idHotel int NOT NULL,
    hotelCity char(45)NOT NULL,
    totalCapacity int NOT NULL,
    
    offPeakPrice int  NOT NULL,
    onPeakPrice int NOT NULL,
    PRIMARY KEY (idHotel)
);







--add data to hotel table (excluding currentCapacity)
INSERT INTO hotel (idHotel,hotelCity,totalCapacity,offPeakPrice,onPeakPrice)
VALUES
(1,"Aberdeen",80,60,140),
(2,"Belfast",80,60,130),
(3,"Birmingham",90,70,150),
(4,"Bristol",90,70,140),
(5,"Cardiff",80,60,120),
(6,"Edingburgh",90,70,160),
(7,"Glasgow",100,70,150),
(8,"London",120,80,200),
(9,"Manchester",110,80,180),
(10,"New Castle",80,60,100),
(11,"Norwich",80,60,100),
(12,"Nottingham",100,70,120),
(13,"Oxford",80,70,180),
(14,"Plymouth",80,50,180),
(15,"Swansea",80,50,120);



--create table roomInfo
CREATE TABLE roomInfo 
(
    idRoomInfo char(10) NOT NULL,
    totalRooms int NOT NULL,
    roomPrice int NOT NULL,
    guestCapacity int NOT NULL,
    PRIMARY KEY (idRoomInfo)
);

--add data to roomInfo table
INSERT INTO roomInfo (idRoomInfo,totalRooms,roomPrice,guestCapacity)
VALUES
("Single",30,0,1),
("Double",50,20,2),
("Family",20,50,6);



--create table customerReservation (for the customer)
CREATE TABLE customerReservation 
(
    idCustomerReservation int AUTO_INCREMENT NOT NULL,
    idUserReservation int NOT NULL,
    idReservation int NOT NULL,
    PRIMARY KEY (idCustomerReservation),
    FOREIGN KEY (idUserReservation) REFERENCES user(idUser),
    FOREIGN KEY (idReservation) REFERENCES reservation(idReservation)
);


--create table reservation
CREATE TABLE reservation 
(
    idReservation int AUTO_INCREMENT NOT NULL,
    hotelInfo int NOT NULL,
    checkInDate DATE NOT NULL,
    checkOutDate DATE NOT NULL,
    dateReserved DATE NOT NULL,
    expired char(3) NOT NULL,
    PRIMARY KEY (idReservation),
    FOREIGN KEY (hotelInfo) REFERENCES hotel(idHotel)

);  

--create guest information 
CREATE TABLE guestInformation
(
    idguestReference int AUTO_INCREMENT NOT NULL,
    idReservation int  NOT NULL,
    customerGuests int NOT NULL,
    customerPrice int NOT NULL,
    roomType char(10) NOT NULL,
    PRIMARY KEY (idguestReference),
    FOREIGN KEY (idReservation) REFERENCES reservation(idReservation)
);




--creates cancelled reservation table
CREATE TABLE cancelledReservation 
(
    idCancelled int AUTO_INCREMENT NOT NULL,
    idReservation int  NOT NULL,
    expired char(3) NOT NULL,
    cancelFee int ,
    PRIMARY KEY (idCancelled),
    FOREIGN KEY (idReservation) REFERENCES reservation(idReservation)
);



--other things
use horizonhotelsdatabase; 

ALTER TABLE  DROP COLUMN password;

ALTER TABLE user DROP COLUMN idUser;


ALTER TABLE user DROP COLUMN fk_Book_User1;

ALTER TABLE user DROP KEY fk_Book_User1;

SHOW CREATE TABLE book;


ALTER TABLE book AUTO_INCREMENT = 1;


ALTER TABLE book 
MODIFY idUser INT NOT NULL AUTO_INCREMENT PRIMARY KEY;

ALTER TABLE book MODIFY COLUMN idUser INT auto_increment primary key;



Alter Table  drop foreign key <constraint_name> 
Alter table <table name> drop key <column name>






SHOW CREATE TABLE `user`;

--shows foreign key constraint 
SELECT
  TABLE_NAME,
  COLUMN_NAME,
  CONSTRAINT_NAME,   -- <<-- the one you want! 
  REFERENCED_TABLE_NAME,
  REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE
  REFERENCED_TABLE_NAME = 'user';



ALTER TABLE user MODIFY COLUMN idUser INT AUTO_INCREMENT=10;

NOT NULL


ALTER TABLE user
ADD COLUMN idUser FIRST NOT NULL AUTO_INCREMENT PRIMARY KEY;

ALTER TABLE user
ADD COLUMN passwordHash VARCHAR(128);

SELECT * FROM reservedroom WHERE idHotel = 4; 

--gets number of prebooked rooms with the same idHotel
SET @result = (SELECT COUNT(*) FROM reservedroom WHERE idHotel = 4);

--prints the variable
SELECT @result;


--30*90/100
--does 30% of totalcapacity in Hotel to get total single rooms
SELECT h.idHotel, r.idRoomInfo, (r.totalRooms*h.totalCapacity)/100 AS totalCapacitySingle
FROM hotel h
    INNER JOIN roominfo r ON r.totalRooms = 30 AND h.idHotel = 4;





--SOLVED--
--e.g 1 single room in Bristol, date is not validated
--USE THIS: all together gets the number of occurences and percent of rooms and sets the result as @rr
SET @rr = (SELECT(SELECT (r.totalRooms*h.totalCapacity)/100  FROM hotel h INNER JOIN roominfo r ON r.totalRooms = 30 AND h.idHotel = 4)
-(SELECT @result));

SELECT @rr
