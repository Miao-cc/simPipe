#!/usr/bin/python
# -*- coding: UTF-8 -*-
import numpy as np
import sqlite3
import os

#operate database
def writedatabase(database, name, dm, period, width, flux, detection, taskid):
    c = database.cursor()
    name = "'"+name+"'"
    sql = " insert into simFiles (name, dm, period, width, flux, detection, taskid) values (%s, %s, %s, %s, %s, %s, %s)" %(name, dm, period, width, flux, detection, taskid)
    c.execute(sql)
    database.commit()
    database.close()

# create database
if os.access("simPipe.db", os.F_OK):
    print "file exist."
else:
    conn = sqlite3.connect('simPipe.db')
    print "Opened database successfully";
    cursor = conn.cursor()
    sql = '''create table simFiles(
            name str,
            dm str,
            period str,
            width str,
            flux str,
            detection str,
            taskid int)'''
    cursor.execute(sql)
    conn.commit()
    conn.close()


