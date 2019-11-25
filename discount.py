# Name : Jess Kwek
# Class: DISM/FT/1B/02


import smtplib

import database.db as db

from sqlite3 import Error

import random
conn = db.connection()

if conn is not None:
    updatecart = """UPDATE users SET discount=0"""
    try:
        cur = conn.cursor()
        cur.execute(updatecart)
        conn.commit()
        cur.close()
    except Error as e:
        print("Something has went wrong on our side, please try again later")
    try:
        cur = conn.cursor()
        cur.execute("""SELECT email FROM users""")
        email_tuple = cur.fetchall()
        email_list = [x[0] for x in email_tuple]
        chosen_one = random.choice(email_list)

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        gmail = "reallydumb555@gmail.com"
        password = "Iamreallyde4d!!!"
        to = [chosen_one]
        subject = "DISCOUNT!!!"
        text = "You are subjected to a 10%% discount when you purchase food at SPAM! Let's have some good food!"
        server.login(gmail, password)
        email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (gmail, ", ".join(to), subject, text)
        server.sendmail(gmail, to, text)
        db.discount(chosen_one,1)
    except Error as e:
        print("Something has went wrong on our side, please try again later")
else:
    print("Something has went wrong on our side, please try again later")
