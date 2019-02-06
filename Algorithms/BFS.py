#BFS.py
import collections as c
from collections import deque
import itertools as iter
import networkx as nx
import math

class Graph(object):
    """A graph object, stored as an adjacency dictionary. Each node in the
    graph is a key in the dictionary. The value of each key is a list of the
    corresponding node's neighbors.

    Attributes:
        dictionary: the adjacency list of the graph.
    """

    def __init__(self, adjacency):
        """Store the adjacency dictionary as a class attribute."""
        self.dictionary = adjacency

    def __str__(self):
        """String representation: a view of the adjacency dictionary.

        Example:
            >>> test = {'A':['B'], 'B':['A', 'C',], 'C':['B']}
            >>> print(Graph(test))
            A: B
            B: A; C
            C: B
        """
        keys,maps =[],[]
        for x in c.Counter(iter.chain.from_iterable(self.dictionary)):    #Set up all of the keys for the dictionary
            keys+=[x]
            maps+=[self.dictionary[x]]
        final = ''
        for x in range(len(keys)):                                        #Loop through the keys and append each value as a string
            final = final + str(keys[x]) + ": "
            for y in maps[x]:
                final = final + str(y)
                if y != maps[x][-1]:
                    final= final+'; '
                else:
                    final = final + '\n'
        return final
        
    def traverseR(self,current,visited,v_queue):
        """Recursive Function for the traverse algorithm
        
        Parameters:
           current: the node we're looking at
            visited: list of visited nodes
            v_queue: queue of nodes to visit
        Returns:
            the list of visited nodes
        """
        visited.append(current)                                            #Look at the current node
        for neighbor in self.dictionary[current]:                          #grab all of it's neighbors
            v_queue.append(neighbor)
        if len(v_queue)==0:
            return visited
        next = v_queue.popleft()                                           #go to one of it's neighbors
        while next in visited:                                             #If we've already visited a node
            if len(v_queue) > 0:
                next = v_queue.popleft()                                   #Look at the next node in line
            else:
                return visited                                             #we reached the end!
        if len(v_queue)==0 and len(self.dictionary) == len(visited):
            return visited
        return self.traverseR(next,visited,v_queue)                        #Go to the next node and see what it has to offer     

    def traverse(self, start):
        """Begin at 'start' and perform a breadth-first search until all
        nodes in the graph have been visited. Return a list of values,
        in the order that they were visited.

        Parameters:
            start: the node to start the search at.
        Returns:
            the list of visited nodes (in order of visitation).
        Raises:
            ValueError: if 'start' is not in the adjacency dictionary.
        Example:
            >>> test = {'A':['B'], 'B':['A', 'C',], 'C':['B']}
            >>> Graph(test).traverse('B')
            ['B', 'A', 'C']
        """
        if start not in self.dictionary:
            raise ValueError("start node is not in the dictionary!")
        return self.traverseR(start,[],deque())

        
    def shortest_path(self, start, target):
        """Begin at the node containing 'start' and perform a breadth-first
        search until the node containing 'target' is found. Return a list
        containg the shortest path from 'start' to 'target'. If either of
        the inputs are not in the adjacency graph, raise a ValueError.

        Parameters:
            start: the node to start the search at.
            target: the node to search for.

        Returns:
            A list of nodes along the shortest path from start to target,
                including the endpoints.

        Example:
            >>> test = {'A':['B', 'F'], 'B':['A', 'C'], 'C':['B', 'D'],
            ...         'D':['C', 'E'], 'E':['D', 'F'], 'F':['A', 'E', 'G'],
            ...         'G':['A', 'F']}
            >>> Graph(test).shortest_path('A', 'G')
            ['A', 'F', 'G']
        """
        if start not in self.dictionary or target not in self.dictionary:
            raise ValueError("Target node or start node not in Dictionary")
        if start == target:
            return [start]
        backMap = {}
        result = self.spR(start,target,[],backMap,deque())
        if result is None:
            return []
        result = [target]
        next = target
        while next != start:
            result += backMap[next]
            next = result[-1]
        return result
        
    def spR(self,current,target,visited,backMap,v_queue):
        """Recursive Function for the shortest path algorithm
        
        Parameters:
            current: the node we're looking at
            visited: list of visited nodes
            v_queue: queue of nodes to visit
        Returns:
            the list of visited nodes
        """
        visited.append(current)                                         #Look at the current node
        for neighbor in self.dictionary[current]:                       #grab all of it's neighbors
            v_queue.append(neighbor)
            if neighbor not in backMap:
                backMap.update({neighbor:[current]})                    #Add a note as to where we came from
            if neighbor == target:
                return target
        if len(v_queue) == 0 and len(self.dictionary) == len(visited):
            return None
        next = v_queue.popleft()                                        #go to one of it's neighbors
        while next in visited:                                          #If we've already visited a node
            if len(v_queue) > 0:
                next = v_queue.popleft()                                #Look at the next node in line
            else:
                return None                                             #we reached the end and there was not a connection
        return self.spR(next,target,visited,backMap,v_queue)            #Go to the next node and see what it has to offer

def convert_to_networkx(dictionary):
    """Convert 'dictionary' to a networkX object and return it."""
    g = nx.Graph()
    for node in dictionary:
        for edge in dictionary[node]:
            g.add_edge(node,edge)
    return g

class BaconSolver(object):
    """Class for solving the Kevin Bacon problem."""

    def __init__(self, filename="movieData.txt"):
        """Initialize the networkX graph with data from the specified
        file. Store the graph as a class attribute. Also store the collection
        of actors in the file as an attribute.
        """
        self.filename=filename
        d={}
        self.actors = set()
        with open(filename,'r') as myfile:
            contents = myfile.readlines()                             #split the file by new lines
            for i in range(len(contents)):
                contents[i]=contents[i].split('/')                    #split the actors up
                contents[i][-1]=contents[i][-1][:-1]                  #erase the \n on the last element
                d.update({contents[i][0]:contents[i][1:]})
                for x in range(1,len(contents[i])):
                    self.actors.add(contents[i][x])
        self.dictionary = nx.Graph(d)

    def path_to_bacon(self, start, target="Bacon, Kevin"):
        """Find the shortest path from 'start' to 'target'."""
        if start not in self.actors or target not in self.actors:
            raise ValueError("An input is not an actor's name!")
        if not nx.has_path(self.dictionary,start,target):
            return math.inf
        return nx.shortest_path(self.dictionary,start,target)

    def bacon_number(self, start, target="Bacon, Kevin"):
        """Return the Bacon number of 'start'."""
        return len(self.path_to_bacon(start,target))//2

    def average_bacon(self, target="Bacon, Kevin"):
        """Calculate the average Bacon number in the data set.
        Note that actors are not guaranteed to be connected to the target.

        Parameters:
            target (str): the node to search the graph for.

        Returns:
            (float): the average (finite) Bacon number
            (int): the number of actors not connected to the target.
        """
        numbers,notConnected = [],0
        for actor in self.actors:
            if nx.has_path(self.dictionary,actor,target):
                numbers += [self.bacon_number(actor)]
            else:
                notConnected += 1
        return sum(numbers)/len(numbers), notConnected
