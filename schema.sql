-- Schema for SQLite3 to be used in Flask

PRAGMA foreign_keys = ON;

-- Table structure for table `author`
CREATE TABLE author (
  authorid INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  status TEXT CHECK(status IN ('Enable', 'Disable')) NOT NULL
);

-- Table structure for table `book`
CREATE TABLE book (
  bookid INTEGER PRIMARY KEY AUTOINCREMENT,
  categoryid INTEGER NOT NULL,
  authorid INTEGER NOT NULL,
  rackid INTEGER NOT NULL,
  name TEXT NOT NULL,
  picture TEXT,
  publisherid INTEGER NOT NULL,
  isbn TEXT NOT NULL,
  no_of_copy INTEGER NOT NULL,
  status TEXT CHECK(status IN ('Enable', 'Disable')) NOT NULL,
  added_on DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_on DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (authorid) REFERENCES author(authorid),
  FOREIGN KEY (categoryid) REFERENCES category(categoryid),
  FOREIGN KEY (publisherid) REFERENCES publisher(publisherid),
  FOREIGN KEY (rackid) REFERENCES rack(rackid)
);

-- Table structure for table `category`
CREATE TABLE category (
  categoryid INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  status TEXT CHECK(status IN ('Enable', 'Disable')) NOT NULL
);

-- Table structure for table `issued_book`
CREATE TABLE issued_book (
  issuebookid INTEGER PRIMARY KEY AUTOINCREMENT,
  bookid INTEGER NOT NULL,
  userid INTEGER NOT NULL,
  issue_date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  expected_return_date DATETIME NOT NULL,
  return_date_time DATETIME,
  status TEXT CHECK(status IN ('Issued', 'Returned', 'Not Return')) NOT NULL,
  FOREIGN KEY (bookid) REFERENCES book(bookid),
  FOREIGN KEY (userid) REFERENCES user(id)
);

-- Table structure for table `publisher`
CREATE TABLE publisher (
  publisherid INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  status TEXT CHECK(status IN ('Enable', 'Disable')) NOT NULL
);

-- Table structure for table `rack`
CREATE TABLE rack (
  rackid INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  status TEXT CHECK(status IN ('Enable', 'Disable')) DEFAULT 'Enable' NOT NULL
);

-- Table structure for table `user`
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT,
  last_name TEXT,
  email TEXT UNIQUE,
  password TEXT NOT NULL,
  role TEXT CHECK(role IN ('admin', 'user')) DEFAULT 'admin'
);


