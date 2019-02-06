# spark.py
import pyspark
from pyspark.sql import SparkSession
import numpy as np
from operator import add


def prob1(filename='mathematicians.csv'):
    """Reads in a csv file of mathematicians and reduces it to the names
    of the female mathemticians born in the 19th century. Returns a list
    of the first 5 of these names.
    """ 
    try:
        sc = pyspark.context.SparkContext()    #Start the spark session
        spark = SparkSession.builder.getOrCreate()
        df = spark.read.option("header",True).csv(filename) #read in the csv
        top5 = df.filter(df['gender']=='female').filter(df['birth_year']>=1800).filter(df['birth_year']<1900).select("name")                           #Filter by what we want to get
        top5.show(5)                            #show the top 5

        return top5.rdd.flatMap(lambda x:x).collect()[:5]
    finally:
        spark.stop()                            #stop the session

def prob2(filename='mathematicians.csv'):
    """Reads in a csv file of mathematicians, groups the
    data by country of citizenship, counts the number of occurrences of each country,
    and returns a list of the top 5 countries and their counts.
    """
    try:
        sc = pyspark.context.SparkContext()                 #Start the spark session
        spark = SparkSession.builder.getOrCreate()
        df = spark.read.option("header",True).csv(filename) #read in the csv
        s = df.groupBy("country").count()
        s=s.sort("count").orderBy("count",ascending=False)  #Sort by the count
        s.show(5)
        return s.rdd.map(lambda x:x[:2]).collect()[:5]      #return the top 5
    finally:
        spark.stop()                                        #stop the session
        
# Problem 3
def sortCount(filename='yoda.txt'):
    """Simple sorted word count function.

    Parameters:
        file (str): text file

    Returns:
        output[:5] (list): the first five (word, count) pairs
    """
    try:
        sc = pyspark.context.SparkContext()     #Start the spark session
        spark = SparkSession.builder.getOrCreate()
        yoda = spark.read.text(filename).rdd    #read the csv
        result = yoda.flatMap(lambda x: x[0].split(" ")).map(
									lambda x: (x,1)).reduceByKey(add).collect()             
												#collect the word count pairs
        spark.stop()                            #stop the session

        return sorted(result,key=lambda x:x[1])[-5:][::-1] #return the top 5


def pi(partitions=2):
    """Simple Monte-Carlo routine to estimate the area of the
    unit circle (i.e. the value of pi).

    Parameters:
        partitions (int): number of partitions to run the calculation with
            (number of partitions specifies the number of nodes to use)

    Returns an estimated value of pi.
    """
    sc = pyspark.context.SparkContext()     #Start the spark session
    spark = SparkSession.builder.getOrCreate()
    n=partitions*10**5
    result = sc.parallelize(range(n),partitions).map(lambda x: np.linalg.norm(np.random.rand(2)*2-1)<=1).collect() #parallelize the MC sampling 
    
    spark.stop()                            #stop the session
    return 4*sum(result)/n                  #return the estimated value of pi
    
    
    
