# solutions.py
import numpy as np
from matplotlib import pyplot as plt
import csv
import sqlite3 as sql

def GetBStudents(db_file="students.db"):
    """Query the database for the list of the names of students who have a
    'B' grade in any course. Return the list.

    Parameters:
        db_file (str): the name of the database to connect to.

    Returns:
        (list): a list of strings, each of which is a student name.
    """
    try:
        with sql.connect(db_file) as conn:
            cur = conn.cursor()
            results = cur.execute("SELECT SI.StudentName "
                                "FROM StudentInfo AS SI INNER JOIN StudentGrades AS SG "
                                "ON SI.StudentID=SG.StudentID "
                                "WHERE SG.Grade == 'B';").fetchall()
            return [x[0] for x in results]    
    except sql.Error as e:
        conn.rollback()
        raise Exception(e)
    else:
        conn.commit()
    finally:
        conn.close()

def GetStudentsMajorsGrades(db_file="students.db"):
    """Query the database for all tuples of the form (Name, MajorName, Grade)
    where 'Name' is a student's name and 'Grade' is their grade in Calculus.
    Only include results for students that are actually taking Calculus, but
    be careful not to exclude students who haven't declared a major.

    Parameters:
        db_file (str): the name of the database to connect to.

    Returns:
        (list): the complete result set for the query.
    """
    try:
        with sql.connect(db_file) as conn:
            cur = conn.cursor()
            return cur.execute("SELECT SI.StudentName, MI.MajorName, SG.Grade "
                                "FROM StudentInfo AS SI "
                                    "LEFT OUTER JOIN MajorInfo AS MI "
                                    "On MI.MajorID=SI.MajorID "
                                    "INNER JOIN StudentGrades AS SG "
                                "ON SI.StudentID=SG.StudentID "
                                "WHERE SG.CourseID = '1';").fetchall()    
    except sql.Error as e:
        conn.rollback()
        raise Exception(e)
    else:
        conn.commit()
    finally:
        conn.close()


def GetBigClasses(db_file="students.db"):
    """Query the database for the list of the names of courses that have at
    least 5 students enrolled in them.

    Parameters:
        db_file (str): the name of the database to connect to.

    Returns:
        ((list): a list of strings, each of which is a course name.
    """
    try:
        with sql.connect(db_file) as conn:
            cur = conn.cursor()
            results = cur.execute("SELECT CI.CourseName "
                                "FROM CourseInfo AS CI "
                                    "INNER JOIN StudentGrades AS SG "
                                    "On CI.CourseID=SG.CourseID "
                                    "GROUP BY CI.CourseName "
                                    "HAVING COUNT(*) >= 5;").fetchall() 
            return [x[0] for x in results]    
    except sql.Error as e:
        conn.rollback()
        raise Exception(e)
    else:
        conn.commit()
    finally:
        conn.close()
    


def GetMajors(db_file="students.db"):
    """Query the given database for tuples of the form (MajorName, N) where N
    is the number of students in the specified major. Sort the results in
    descending order by the counts N, then in alphabetic order by MajorName.

    Parameters:
        db_file (str): the name of the database to connect to.

    Returns:
        (list): the complete result set for the query.
    """
    try:
        with sql.connect(db_file) as conn:
            cur = conn.cursor()
            return cur.execute("SELECT MI.MajorName, COUNT(*) AS num_students "
                                "FROM StudentInfo AS SI "
                                    "LEFT OUTER JOIN MajorInfo AS MI "
                                    "On MI.MajorID=SI.MajorID "
                                    "GROUP BY MI.MajorName "
                                    "ORDER BY num_students DESC, MI.MajorName ASC;").fetchall()    
    except sql.Error as e:
        conn.rollback()
        raise Exception(e)
    else:
        conn.commit()
    finally:
        conn.close()
    


def GetStudentsInMajors(db_file="students.db"):
    """Query the database for tuples of the form (StudentName, MajorName) where
    the last name of the specified student begins with the letter C.

    Parameters:
        db_file (str): the name of the database to connect to.

    Returns:
        (list): the complete result set for the query.
    """
    try:
        with sql.connect(db_file) as conn:
            cur = conn.cursor()
            return cur.execute("SELECT SI.StudentName, MI.MajorName "
                                "FROM StudentInfo AS SI "
                                    "LEFT OUTER JOIN MajorInfo AS MI "
                                    "On MI.MajorID=SI.MajorID "
                                    "WHERE StudentName LIKE '% C%';").fetchall()    
    except sql.Error as e:
        conn.rollback()
        raise Exception(e)
    else:
        conn.commit()
    finally:
        conn.close()


def GetStudentGPA(db_file="students.db"):
    """Query the database for tuples of the form (StudentName, N, GPA) where N
    is the number of courses that the specified student is in and 'GPA' is the
    grade point average of the specified student according to the following
    point system.

        A+, A  = 4.0    B  = 3.0    C  = 2.0    D  = 1.0
            A- = 3.7    B- = 2.7    C- = 1.7    D- = 0.7
            B+ = 3.4    C+ = 2.4    D+ = 1.4

    Order the results from greatest GPA to least.

    Parameters:
        db_file (str): the name of the database to connect to.

    Returns:
        (list): the complete result set for the query.
    """
    try:
        with sql.connect(db_file) as conn:
            cur = conn.cursor()
            return cur.execute("SELECT SI.StudentName, COUNT(*) AS N, AVG(CASE Grade "
                                "WHEN 'A+' THEN 4.0 "
                                "WHEN 'A' THEN 4.0 "
                                "WHEN 'A-' THEN 3.7 "
                                "WHEN 'B+' THEN 3.4 "
                                "WHEN 'B' THEN 3.0 "
                                "WHEN 'B-' THEN 2.7 "
                                "WHEN 'C+' THEN 2.4 "
                                "WHEN 'C' THEN 2.0 "
                                "WHEN 'C-' THEN 1.7 "
                                "WHEN 'D+' THEN 1.4 "
                                "WHEN 'D' THEN 1.0 "
                                "WHEN 'D-' THEN 0.7 END) AS GPA "
                                "FROM StudentInfo AS SI "
                                    "LEFT OUTER JOIN StudentGrades AS SG "
                                    "On SG.StudentID=SI.StudentID "
                                    "GROUP BY StudentName "
                                    "ORDER BY GRADE ASC;").fetchall()    
    except sql.Error as e:
        conn.rollback()
        raise Exception(e)
    else:
        conn.commit()
    finally:
        conn.close()
