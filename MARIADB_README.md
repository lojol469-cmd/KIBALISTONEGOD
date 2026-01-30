# Portable MariaDB Setup

This project includes a portable MariaDB setup for database functionality without requiring system installation.

## Database Configuration

The application is configured to use MariaDB with the following settings:
- Host: localhost
- Port: 3306
- User: root
- Password: (empty)
- Database: excel_app

## Starting MariaDB

To start the MariaDB server:
1. Run `start_mariadb.bat` from the project root directory
2. The server will start in the background
3. Press any key in the command window to stop the server

## Database Initialization

The application will automatically create the necessary tables when it first connects to the database. The tables include:
- `app_data`: Stores application configuration data
- `audit_logs`: Stores user action logs
- `corbeille`: Stores deleted items

## Fallback

If MariaDB is not available, the application will automatically fall back to using SQLite for data storage.

## Files

- `mariadb_portable/`: Contains the portable MariaDB installation
- `start_mariadb.bat`: Script to start/stop the MariaDB server
- `excel/.env`: Contains database connection settings