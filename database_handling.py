#!/usr/bin/python3
"""
Module: database_handling.py

Description:
This script is designed to handle the database operations for the websraper.

Author:
[Krzysztof H.]

Date:
[18.07.2023]

Python Version:
[3.11.1]

Dependencies:
- sqlite3

Note:
- The script is meant to be imported.
"""
import sqlite3
from sqlite3 import Error


def create_connection():
    """
    Create a connection to the SQLite database.

    Returns:
        conn: A connection object to the database if successful, otherwise None.
    """
    conn = None
    try:
        conn = sqlite3.connect("messages.db")
        print("Connection to database successful")
        return conn
    except Error as exception:
        print(f"Error connecting to SQLite database: {exception}")
        return None


def insert_data(table, *args):
    """
    Insert data into the specified table.

    Args:
        table (str): The name of the table to insert data into
        ("news_table" or "redirected_table").
        *args (tuple): The data to be inserted into the table.
    """
    conn = create_connection()
    try:
        cursor = conn.cursor()

        if table == "news_table":
            query = f"""
                INSERT INTO {table} (link, tag, date, topic, photo, message_lead, author)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            values = args
        elif table == "redirected_table":
            query = f"""
                INSERT INTO {table} (link)
                VALUES (?)
            """
            values = args
        else:
            print(f"Unknown table name: {table}")
            return

        cursor.execute(query, values)
        conn.commit()
        print("Data inserted successfully")
    except Error as exception:
        print(f"Error inserting data: {exception}")
    finally:
        close_connection(conn)


def fetch_links(table):
    """
    Fetch links from the specified table.

    Args:
        table (str): The name of the table to fetch links from ("news_table" or "redirected_table").

    Returns:
        list: A list of link strings from the specified table.
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT link FROM {table}")
    database_list = []
    for row in cursor.fetchall():
        database_list.append(row[0])
    close_connection(conn)
    print(f"Fetching links from {table}")
    return database_list


def create_tables():
    """
    Create the necessary tables if they don't already exist.
    """
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS news_table (
                id INTEGER PRIMARY KEY,
                link TEXT UNIQUE,
                tag TEXT,
                date TEXT,
                       topic TEXT,
                       photo TEXT,
                       message_lead TEXT,
                       author TEXT
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS redirected_table (
                id INTEGER PRIMARY KEY,
                link TEXT UNIQUE,
                redirected TEXT DEFAULT 'Redirected'
            )
        """
        )
        conn.commit()
        print("Tables created succesfully")
    except Error as exception:
        print(f"Error creating tables: {exception}")
    finally:
        close_connection(conn)


def tables_exist():
    """
    Check if 'news_table' and 'redirected_table' exist in the database.

    Returns:
        bool: True if both tables exist, False otherwise.
    """
    conn = create_connection()
    try:
        cursor = conn.cursor()

        # Check if the 'news_table' exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='news_table'"
        )
        news_table_exists = cursor.fetchone() is not None

        # Check if the 'redirected_table' exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='redirected_table'"
        )
        redirected_table_exists = cursor.fetchone() is not None
        print("Tables already exist.")
        return news_table_exists and redirected_table_exists

    except Error as exception:
        print(f"Error checking table existence: {exception}")
        return False

    finally:
        close_connection(conn)


def close_connection(conn):
    """
    Close the connection to the database.

    Args:
        conn: The connection object to be closed.
    """
    if conn is not None:
        conn.close()
        print("Disconnected from database")
