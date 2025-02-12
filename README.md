# NTUA Software Engineering 2024

Toll System API implementation

---

# Toll System Management API & CLI

## Overview

This project provides a **RESTful Web API** and a **Command-Line Interface (CLI)** for managing interoperability of toll stations on highways. It allows administrators and users to interact with toll-related data such as vehicle passes, station information, and charges.
It also includes a web application (HTML) as a use case.

## System Architecture

The system consists of:
- **A RESTful API** built with Flask, handling toll station data and user authentication.
- **A CLI tool** for command-line interaction with the API.
- **A MySQL database** to store all toll station and pass information.
- **JWT-based authentication** for user access control.

---

## 1. REST API

The REST API is hosted at:

```
http://localhost:9115/api
```

### 1.1 Authentication

#### Login
- **Endpoint**: `POST /login`
- **Request**:
  ```sh
  curl -X POST http://localhost:9115/api/login -d "username=admin&password=adminpass"
  ```
- **Response**:
  ```json
  { "token": "your-access-token" }
  ```

#### Logout
- **Endpoint**: `POST /logout`
- **Request**:
  ```sh
  curl -X POST http://localhost:9115/api/logout -H "X-OBSERVATORY-AUTH: Bearer your-access-token"
  ```

---

### 1.2 Admin Endpoints

#### Health Check
- **Endpoint**: `GET /admin/healthcheck`
- **Response**:
  ```json
  { "status": "OK", "dbconnection": "Connected", "n_stations": 10, "n_passes": 100 }
  ```

#### Reset Toll Stations
- **Endpoint**: `POST /admin/resetstations`
- **Response**:
  ```json
  { "status": "OK" }
  ```

#### Reset Passes
- **Endpoint**: `POST /admin/resetpasses`
- **Response**:
  ```json
  { "status": "OK" }
  ```

#### Add Passes (CSV Upload)
- **Endpoint**: `POST /admin/addpasses`
- **Request**:
  ```sh
  curl -X POST -H "X-OBSERVATORY-AUTH: Bearer your-access-token" \
       -F "file=@passes.csv" http://localhost:9115/api/admin/addpasses
  ```
- **Response**:
  ```json
  { "status": "OK" }
  ```

#### User Management
- **List Users**: `GET /admin/users`
- **Create/Modify User**: `POST /admin/usermod`
  ```json
  { "username": "newuser", "password": "newpass", "operator": "operator1" }
  ```

---

### 1.3 Core Functional Endpoints

#### Get Passes for a Toll Station
- **Endpoint**: `GET /tollStationPasses/:tollStationID/:date_from/:date_to`
- **Example Request**:
  ```sh
  curl -H "X-OBSERVATORY-AUTH: Bearer your-access-token" \
       http://localhost:9115/api/tollStationPasses/NAO01/20240101/20240131
  ```
- **Response**:
  ```json
  {
    "stationID": "NAO01",
    "nPasses": 3,
    "passList": [
      { "passID": "P001", "timestamp": "2024-01-10 12:00", "passCharge": 1.5 }
    ]
  }
  ```

#### Pass Analysis Between Operators
- **Endpoint**: `GET /passAnalysis/:stationOpID/:tagOpID/:date_from/:date_to`
- **Response**:
  ```json
  {
    "stationOpID": "O1",
    "tagOpID": "O2",
    "nPasses": 10,
    "passList": [
      { "passID": "P001", "stationID": "S001", "passCharge": 2.5 }
    ]
  }
  ```

#### Passes Cost Between Operators
- **Endpoint**: `GET /passesCost/:tollOpID/:tagOpID/:date_from/:date_to`
- **Response**:
  ```json
  { "nPasses": 50, "passesCost": 125.5 }
  ```

#### Charges By Operator
- **Endpoint**: `GET /chargesBy/:tollOpID/:date_from/:date_to`
- **Response**:
  ```json
  {
    "tollOpID": "O1",
    "vOpList": [
      { "visitingOpID": "O2", "nPasses": 20, "passesCost": 50.0 }
    ]
  }
  ```

---

## 2. Command-Line Interface (CLI)

The CLI provides an alternative way to interact with the API.

### 2.1 Setup

Make sure you have `cli.py` in your project directory and run:
```sh
chmod +x cli.py
```
Usage:
```sh
./cli.py <command> [options]
```

### 2.2 CLI Commands

#### Login
```sh
./cli.py login --username admin --password adminpass
```

#### Logout
```sh
./cli.py logout
```

#### Health Check
```sh
./cli.py healthcheck
```

#### Reset Passes
```sh
./cli.py resetpasses
```

#### Reset Toll Stations
```sh
./cli.py resetstations
```

#### List Users (Admin only)
```sh
./cli.py admin --users
```

#### Add Passes from CSV
```sh
./cli.py admin --addpasses --source passes.csv
```

#### Get Toll Station Passes
```sh
./cli.py tollstationpasses --station NAO01 --from 20240101 --to 20240131 --format json
```

#### Get Pass Analysis
```sh
./cli.py passanalysis --stationop O1 --tagop O2 --from 20240101 --to 20240131 --format json
```

#### Get Passes Cost
```sh
./cli.py passescost --stationop O1 --tagop O2 --from 20240101 --to 20240131 --format csv
```

#### Get Charges by Operator
```sh
./cli.py chargesby --opid O1 --from 20240101 --to 20240131 --format csv
```

---

## 3. Database Schema

The system uses a **MySQL** database with the following tables:

### `users`
| id | username | password_hash | operator |
|----|---------|--------------|----------|

### `toll_stations`
| toll_id | name | operator |
|---------|------|----------|

### `passes`
| id | timestamp | toll_id | tag_ref | tag_home_id | charge |
|----|-----------|--------|---------|-------------|--------|

---

## 4. Installation & Setup

### 4.1 Prerequisites
- Python 3.8+
- MySQL Server
- Flask, Flask-JWT-Extended, Flask-CORS, Flask-Bcrypt, MySQL-Connector

### 4.2 Install Dependencies
```sh
pip install flask flask-jwt-extended flask-cors flask-bcrypt mysql-connector-python
```

### 4.3 Database Setup
```sql
CREATE DATABASE toll_system;
USE toll_system;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    operator VARCHAR(50)
);

CREATE TABLE toll_stations (
    toll_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(50),
    operator VARCHAR(50)
);

CREATE TABLE passes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME,
    toll_id VARCHAR(10),
    tag_ref VARCHAR(50),
    tag_home_id VARCHAR(50),
    charge FLOAT
);
```

### 4.4 Run the API
```sh
python app.py
```

---

## 5. Conclusion

This system provides a full-fledged REST API and CLI for toll station interoperability management. It supports authentication, station and pass data retrieval, and admin tools for managing the system.

---
