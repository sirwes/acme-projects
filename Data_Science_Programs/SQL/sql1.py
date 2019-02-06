# sql1.py
import numpy as np
from matplotlib import pyplot as plt
import csv
import sqlite3 as sql

def student_db(db_file="students.db", student_info="student_info.csv",
                                      student_grades="student_grades.csv"):
    """Connect to the database db_file (or create it if it doesn’t exist).
    Drop the tables MajorInfo, CourseInfo, StudentInfo, and StudentGrades from
    the database (if they exist). Recreate the following (empty) tables in the
    database with the specified columns.

        - MajorInfo: MajorID (integers) and MajorName (strings).
        - CourseInfo: CourseID (integers) and CourseName (strings).
        - StudentInfo: StudentID (integers), StudentName (strings), and
            MajorID (integers).
        - StudentGrades: StudentID (integers), CourseID (integers), and
            Grade (strings).

    Next, populate the new tables with the following data and the data in
    the specified 'student_info' 'student_grades' files.

                MajorInfo                         CourseInfo
            MajorID | MajorName               CourseID | CourseName
            -------------------               ---------------------
                1   | Math                        1    | Calculus
                2   | Science                     2    | English
                3   | Writing                     3    | Pottery
                4   | Art                         4    | History

    Finally, in the StudentInfo table, replace values of −1 in the MajorID
    column with NULL values.

    Parameters:
        db_file (str): The name of the database file.
        student_info (str): The name of a csv file containing data for the
            StudentInfo table.
        student_grades (str): The name of a csv file containing data for the
            StudentGrades table.
    """
    try:
        with sql.connect(db_file) as conn:
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS MajorInfo")
            cur.execute("DROP TABLE IF EXISTS CourseInfo")
            cur.execute("DROP TABLE IF EXISTS StudentInfo")
            cur.execute("DROP TABLE IF EXISTS StudentGrades")
            cur.execute("CREATE TABLE MajorInfo (MajorID INTEGER, MajorName TEXT)")
            cur.execute("CREATE TABLE CourseInfo (CourseID INTEGER, CourseName TEXT)")
            cur.execute("CREATE TABLE StudentInfo (StudentID INTEGER, StudentName TEXT, MajorID INTEGER)")
            cur.execute("CREATE TABLE StudentGrades (StudentID INTEGER, CourseID INTEGER, Grade TEXT)")
            majorrows = [(1,'Math'),(2,'Science'),(3,'Writing'),(4,'Art')]      
            cur.executemany("INSERT INTO MajorInfo VALUES(?,?);",majorrows)
            courserows = [(1,'Calculus'),(2,'English'),(3,'Pottery'),(4,'History')]            
            cur.executemany("INSERT INTO CourseInfo VALUES (?,?);",courserows)
            with open(student_info,'r') as infile:
                sirows = list(csv.reader(infile))            
                cur.executemany("INSERT INTO StudentInfo VALUES (?,?,?);",sirows)
                cur.execute("UPDATE StudentInfo SET MajorID=NULL WHERE MajorID==-1;")
            with open(student_grades,'r') as infile:
                sgrows = list(csv.reader(infile))            
                cur.executemany("INSERT INTO StudentGrades VALUES (?,?,?);",sgrows)     
    except sql.Error as e:
        conn.rollback()
        print(e)
    else:
        conn.commit()
    finally:
        conn.close()
    

def earthquakes_db(db_file="earthquakes.db", data_file="us_earthquakes.csv"):
    """Connect to the database db_file (or create it if it doesn’t exist).
    Drop the USEarthquakes table if it already exists, then create a new
    USEarthquakes table with schema
    (Year, Month, Day, Hour, Minute, Second, Latitude, Longitude, Magnitude).
    Populate the table with the data from 'data_file'.

    For the Minute, Hour, Second, and Day columns in the USEarthquakes table,
    change all zero values to NULL. These are values where the data originally
    was not provided.

    Parameters:
        db_file (str): The name of the database file.
        data_file (str): The name of a csv file containing data for the
            USEarthquakes table.
    """
    try:
        with sql.connect(db_file) as conn:
            cur=conn.cursor()
            cur.execute("DROP TABLE IF EXISTS USEarthquakes")
            cur.execute("CREATE TABLE USEarthquakes (Year INTEGER, Month INTEGER, Day INTEGER, Hour INTEGER, Minute INTEGER, Second INTEGER, Latitude REAL, Longitude REAL, Magnitude REAL);")
            with open(data_file) as infile:
                rows = list(csv.reader(infile))
                cur.executemany("INSERT INTO USEarthquakes Values(?,?,?,?,?,?,?,?,?);",rows)
                cur.execute("DELETE FROM USEarthquakes WHERE Magnitude==0;")
                cur.execute("UPDATE USEarthquakes SET Day=NULL WHERE Day==0;")
                cur.execute("UPDATE USEarthquakes SET Hour=NULL WHERE Hour==0;")
                cur.execute("UPDATE USEarthquakes SET Minute=NULL WHERE Minute==0;")
                cur.execute("UPDATE USEarthquakes SET Second=NULL WHERE Second==0;")
    except sql.Error as e:
        print(e)
        conn.rollback()
    else:
        conn.commit()
    finally:
        conn.close()

def GetGoodStudents(db_file="students.db"):
    """Query the database for all tuples of the form (StudentName, CourseName)
    where that student has an 'A' or 'A+'' grade in that course. Return the
    list of tuples.

    Parameters:
        db_file (str): the name of the database to connect to.

    Returns:
        (list): the complete result set for the query.
    """
    try:
        with sql.connect(db_file) as conn:
            cur = conn.cursor()
            return cur.execute("SELECT SI.StudentName, CI.CourseName "
                                "FROM StudentInfo AS SI, StudentGrades AS SG, CourseInfo AS CI "
                                "WHERE SI.StudentID == SG.StudentID AND (SG.Grade=='A' OR SG.Grade=='A+') AND SG.CourseID==CI.CourseID;").fetchall()
    except sql.Error as e:
        conn.rollback()
        raise Exception(e)
    else:
        conn.commit()
    finally:
        conn.close()


def AvgMagnitude(db_file="earthquakes.db"):
    """Create a single figure with two subplots: a histogram of the magnitudes
    of the earthquakes from 1800-1900, and a histogram of the magnitudes of the
    earthquakes from 1900-2000. Also calculate and return the average magnitude
    of all of the earthquakes in the database.

    Parameters:
        db_file (str): the name of the database to connect to.

    Returns:
        (float): The average magnitude of all earthquakes in the database.
    """
    try:
        with sql.connect(db_file) as conn:
            cur = conn.cursor()
            avgmag = cur.execute("SELECT Count(Magnitude), SUM(Magnitude) FROM USEarthquakes").fetchall()
            plt.subplot(121)
            plt.hist(np.ravel(cur.execute("SELECT Magnitude FROM USEarthquakes WHERE Year BETWEEN 1799 AND 1900;").fetchall()))
            plt.title("19th Century")
            plt.xlabel("Magnitude")
            plt.ylabel("Number of Earthquakes")
            plt.subplot(122)
            plt.hist(np.ravel(cur.execute("SELECT Magnitude FROM USEarthquakes WHERE Year BETWEEN 1899 AND 2000;").fetchall()))
            plt.title("20th Century")
            plt.xlabel("Magnitude")
            plt.show()
            return avgmag[0][1]/avgmag[0][0]
    except sql.Error as e:
        raise Exception(e)
    else:
        conn.commit()
    finally:
        conn.close()