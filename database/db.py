# Name : Jess Kwek
# Class: DISM/FT/1B/02


import sqlite3
from sqlite3 import Error
import hashlib
import random
import string
import os
from validate_email import validate_email
# all function names here are what they do

def connection():
    conn = None
    try:
        conn = sqlite3.connect("database/all_da_data.db")
    except Error as e:
        print(e)

    return conn


def create(conn, command, details):
    cur = conn.cursor()
    cur.execute(command, details)
    conn.commit()


def getrows(conn, command, details):
    try:
        cur = conn.cursor()
        cur.execute(command, details)
        return cur.fetchall()
    except Error as e:
        print(e)
        return None


def create_database():
    conn = connection()
    create_user_table = """ CREATE TABLE IF NOT EXISTS users(  
                                username text NOT NULL PRIMARY KEY,
                                password text NOT NULL,
                                salt text NOT NULL,
                                email text NOT NULL,
                                discount integer
                            );"""
    create_food_table = """ CREATE TABLE IF NOT EXISTS food(
                                name text NOT NULL PRIMARY KEY,
                                price real NOT NULL
                                
                            );"""
    create_orders_table = """ CREATE TABLE IF NOT EXISTS cart(
                                name text NOT NULL,
                                food_name text NOT NULL,
				quantity integer NOT NULL
                                );"""
    create_favourites_table = """ CREATE TABLE IF NOT EXISTS favourites(
                                    name text NOT NULL PRIMARY KEY,
                                    food_name text NOT NULL
                                    );"""
    listt = [
        create_user_table, create_food_table, create_orders_table,
        create_favourites_table
    ]
    if conn is not None:
        try:
            for x in listt:
                create(conn, x, "")
            return True
        except Error as e:
            print(e)
            return False


def sign_up(name, email, password):
    def salt_gen():
        saltgen = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(saltgen) for i in range(15))

    def user_exist(username):
        check_user = """ SELECT username FROM users WHERE username=?"""
        cur = conn.cursor()
        cur.execute(check_user, (username, ))
        if cur.fetchone() is not None:
            return True
        else:
            return False

    def email_exist(email):
        check_email = """ SELECT email FROM users WHERE email=?"""
        cur = conn.cursor()
        cur.execute(check_email, (email, ))
        if cur.fetchone() is not None:
            return True
        else:
            return False

    conn = connection()
    if conn is not None:
        exist = (user_exist(name) or email_exist(email))
        if exist:
            return "existed"
        else:
            salt = salt_gen()
            new_password = password + salt
            hashed = hashlib.sha3_512(new_password.encode('UTF-8')).hexdigest()
            details = (name, hashed, salt, email, 0)
            create_user = """INSERT into users(username,password,salt,email,discount)
                     VALUES(?,?,?,?,?)"""
            initialise_fav = """INSERT into favourites(name,food_name) VALUES(?,?)"""
            try:
                create(conn, create_user, details)
                create(conn, initialise_fav, (name, ""))
                return "Yes"
            except Error as e:
                print(e)
                return "No"
    else:
        return False


def sign_in(name, password):
    def get_salt(username):
        cur = conn.cursor()
        cur.execute("""SELECT salt FROM users WHERE username=?""",
                    (username, ))
        return cur.fetchone()

    def user_exist(username):
        check_user = """ SELECT username FROM users WHERE username=?"""
        cur = conn.cursor()
        cur.execute(check_user, (username, ))
        if cur.fetchone() is not None:
            return True
        else:
            return False

    conn = connection()
    check = user_exist(name)
    if check:
        hey = get_salt(name)[0]
        combined = password + hey
        hashed = hashlib.sha3_512(combined.encode('UTF-8')).hexdigest()
        login = """SELECT username,password FROM users WHERE username=? AND password=?"""
        cur = conn.cursor()
        cur.execute(login, (name, hashed))
        if cur.fetchone() is not None:
            return True
        else:
            return False
    else:
        return False


def get_food():
    conn = connection()
    if conn is not None:
        command = """SELECT * FROM food"""
        return getrows(conn, command, "")
    else:
        return None


def get_fav(username):
    conn = connection()
    if conn is not None:
        command = """SELECT food_name from favourites WHERE name=?"""
        return getrows(conn, command, (username, ))
    else:
        return None


def check_fav(username, food):
    conn = connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute("""SELECT food_name FROM favourites WHERE name=?""",
                    (username, ))
        hello = cur.fetchall()
        try:
            everything = hello[0][0].split(",")
        except IndexError:
            return False
        if food in everything:
            return True
        else:
            return False


def check_cart(username, food):
    conn = connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(
            """SELECT food_name FROM cart WHERE name=? AND food_name=?""",
            (username, food))
        hello = cur.fetchone()
        if hello is not None:
            return True
        else:
            return False


def overwrite(username, food):
    conn = connection()
    if conn is not None:
        try:
            cur = conn.cursor()
            cur.execute("""DELETE from cart WHERE name=? AND food_name=?""",
                        (username, food))
            conn.commit()
        except Error as e:
            print(e)


def order(username, favourites, food, quantity, fav):
    conn = connection()
    if conn is not None:
        cur = conn.cursor()
        order = """INSERT into cart(name,food_name,quantity)
                    VALUES(?,?,?)"""
        if fav:
            update_fav(username, favourites)
        try:
            create(conn, order, (username, food, quantity))
        except Error as e:
            print(e)
            print(
                "Something has went wrong on our side, please try again later")


def update_fav(username, favourites):
    conn = connection()
    if conn is not None:
        add_fav = """UPDATE favourites SET food_name=? WHERE name=?"""
        try:
            create(conn, add_fav, (favourites, username))
        except Error as e:
            print(e)
            print(
                "Something has went wrong on our side, please try again later."
            )
    else:
        print("Something has went wrong on our side, please try again later")


def get_cart(username):
    conn = connection()
    if conn is not None:
        getcart = """ SELECT food_name,quantity from cart WHERE name=?"""
        return getrows(conn, getcart, (username, ))
    else:
        return None


def update_cart(username, food, quantity):
    conn = connection()
    if conn is not None:
        updatecart = """UPDATE cart SET quantity=? WHERE name=? AND food_name=?"""
        try:
            create(conn, updatecart, (quantity, username, food))
        except Error as e:
            print(e)
            print(
                "Something has went wrong on our side, please try again later."
            )
    else:
        print("Something has went wrong on our side, please try again later")


def clear_cart(username):
    conn = connection()
    if conn is not None:
        del_cart = """DELETE FROM cart WHERE name=?"""
        try:
            cur = conn.cursor()
            cur.execute(del_cart, (username, ))
            conn.commit()
        except Error as e:
            print(
                "Something has went wrong on our side, please try again later")
    else:
        print("Something has went wrong on our side, please try again later")


def discount(username, num):
    conn = connection()
    if conn is not None:

        try:
            cur = conn.cursor()
            cur.execute("""UPDATE users SET discount=? WHERE email=?""", (num, username))
            conn.commit()
        except Error as e:
            print(
                "Something has went wrong on our side, please try again later")
    else:
        print("Something has went wrong on our side, please try again later")


def check_discount(username):
    conn = connection()
    if conn is not None:
        get_discount = """SELECT discount FROM users WHERE username=?"""
        try:
            cur = conn.cursor()
            cur.execute(get_discount, (username, ))
            return cur.fetchone()
        except Error as e:
            print(
                "Something has went wrong on our side, please try again later")
    else:
        print("Something has went wrong on our side, please try again later")
