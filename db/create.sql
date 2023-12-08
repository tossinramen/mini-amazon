-- Feel free to modify this file to match your development goal.
-- Here we only create 3 tables for demo purpose.

CREATE TABLE Users (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    address VARCHAR(500),
    balance DECIMAL(12,2) NOT NULL DEFAULT 0.00
);

CREATE TABLE Products (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    name VARCHAR(255) UNIQUE NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    description VARCHAR(255) NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    category VARCHAR(255) NOT NULL,
    tag VARCHAR(255) NOT NULL,
    subtag VARCHAR(255) NOT NULL,
    image_url VARCHAR(255) NOT NULL
);

CREATE TABLE Purchases (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL REFERENCES Users(id),
    time_purchased timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);
CREATE TABLE Product_Rating (
    uid INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    description VARCHAR(255) NOT NULL,
    upvotes INT NOT NULL,
    downvotes INT NOT NULL,
    stars INT CHECK (stars >= 1 AND stars <= 5), 
    time_reviewed timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    primary key (uid, pid)
);

CREATE TABLE Seller_Rating (
    uid INT NOT NULL REFERENCES Users(id),
    sid INT NOT NULL REFERENCES Users(id),
    description VARCHAR(255) NOT NULL,
    upvotes INT NOT NULL,
    downvotes INT NOT NULL,
    stars INT CHECK (stars >= 1 AND stars <= 5), 
    time_reviewed timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    primary key (uid, sid)
);
CREATE TABLE Seller_Inventory (
    uid INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    quantity INT NOT NULL,
    PRIMARY KEY (uid, pid)
);
CREATE TABLE Sellers (
    uid INT NOT NULL REFERENCES Users(id) PRIMARY KEY,
    avg_rating FLOAT NOT NULL
);
CREATE TABLE Wishes (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    time_added timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);
CREATE TABLE Carts (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL REFERENCES Users(id)
);



CREATE TABLE CartLineItems (    
    id INT NOT NULL REFERENCES Carts(id),
    sid INT NOT NULL REFERENCES Sellers(uid),
    pid INT NOT NULL REFERENCES Products(id),
    qty INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (id, sid, pid)
);

CREATE TABLE BoughtLineItems (    
    id INT NOT NULL REFERENCES Purchases(id),
    sid INT NOT NULL REFERENCES Sellers(uid),
    pid INT NOT NULL REFERENCES Products(id),
    qty INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    fulfilled BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (id, sid, pid)
);




