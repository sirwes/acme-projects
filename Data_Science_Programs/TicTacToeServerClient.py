# TicTacToeServerClient.py
import sys
import traceback
import random
import json
import socket
import re
import operator
from matplotlib import pyplot as plt


def ExtractData(filename="nyc_traffic.json"):
    """Load the data from the specified JSON file. Look at the first few
    entries of the dataset and decide how to gather information about the
    cause(s) of each accident. Make a readable, sorted bar chart showing the
    total number of times that each of the 7 most common reasons for accidents
    are listed in the data set.
    """
    #open the file
    with open(filename,'r') as infile:
    	data = json.load(infile)
    reasons = dict()
    #loop through the points to grab all of the reasons and update the count in the dictionary
    for point in data:
    	try:
    	    reason1 = point["contributing_factor_vehicle_1"]
    	    if reason1 not in reasons:
    	        reasons[reason1] = 0
    	    reasons[reason1] += 1
    	except:
    	    pass
    	try:
    	    reason2 = point["contributing_factor_vehicle_2"]
    	    if reason2 not in reasons:
    	        reasons[reason2] = 0 
    	    reasons[reason2] +=1
    	except:
    	    pass   
    #sort the dictionary by most counted to least
    sortedReasons = sorted(reasons.items(),key=operator.itemgetter(1),reverse = True)
    top7 =dict()
    i=0
    #get the top 7
    for r in sortedReasons:
        top7[r[0]] = r[1] 
        i+=1
        if i > 6:
            break
    #plot it as a bar graph
    plt.barh(range(7),top7.values(),align='center')
    plt.yticks(range(7),top7.keys())
    plt.tight_layout()
    plt.title("Top 7 Reasons for Car Crashes in NYC")
    plt.xlabel("Reason for Crash")
    plt.ylabel("Number of Crashes")
    plt.show()
    


class TicTacToe:
    def __init__(self):
        """Initialize an empty board. The O's go first."""
        self.board = [[' ']*3 for _ in range(3)]
        self.turn, self.winner = "O", None

    def move(self, i, j):
        """Mark an O or X in the (i,j)th box and check for a winner."""
        if self.winner is not None:
            raise ValueError("the game is over!")
        elif self.board[i][j] != ' ':
            raise ValueError("space ({},{}) already taken".format(i,j))
        self.board[i][j] = self.turn

        # Determine if the game is over.
        b = self.board
        if any(sum(s == self.turn for s in r)==3 for r in b):
            self.winner = self.turn     # 3 in a row.
        elif any(sum(r[i] == self.turn for r in b)==3 for i in range(3)):
            self.winner = self.turn     # 3 in a column.
        elif b[0][0] == b[1][1] == b[2][2] == self.turn:
            self.winner = self.turn     # 3 in a diagonal.
        elif b[0][2] == b[1][1] == b[2][0] == self.turn:
            self.winner = self.turn     # 3 in a diagonal.
        else:
            self.turn = "O" if self.turn == "X" else "X"

    def empty_spaces(self):
        """Return the list of coordinates for the empty boxes."""
        return [(i,j) for i in range(3) for j in range(3)
                                        if self.board[i][j] == ' ' ]
    def __str__(self):
        return "\n---------\n".join(" | ".join(r) for r in self.board)



class TicTacToeEncoder(json.JSONEncoder):
    """A custom JSON Encoder for TicTacToe objects."""
    def default(self,obj):
        if not isinstance(obj,TicTacToe):
            raise TypeError("Expected a TicTacToe Object for encoding")
        return {'dtype':'TicTacToe','board':obj.board,'turn':obj.turn,'winner':obj.winner}



def tic_tac_toe_decoder(obj):
    """A custom JSON decoder for TicTacToe objects."""
    if 'dtype' in obj:
        if obj['dtype'] != "TicTacToe" or 'board' not in obj or 'turn' not in obj or 'winner' not in obj:
            raise ValueError("Expected a JSON message from TicTacToeEncoder")
            #if a valid object, put the info into a new game
        game =  TicTacToe()        
        game.board = obj['board']
        game.turn = obj['turn']
        game.winner = obj['winner']
        return game 
    raise ValueError("expected a JSON message from TicTacToeEncoder")


def mirror_server(server_address=("0.0.0.0", 33333)):
    """A server for reflecting strings back to clients in reverse order."""
    print("Starting mirror server on {}".format(server_address))

    # Specify the socket type, which determines how clients will connect.
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(server_address)    # Assign this socket to an address.
    server_sock.listen(1)               # Start listening for clients.

    while True:
        # Wait for a client to connect to the server.
        print("\nWaiting for a connection...")
        connection, client_address = server_sock.accept()

        try:
            # Receive data from the client.
            print("Connection accepted from {}.".format(client_address))
            in_data = connection.recv(1024).decode()    # Receive data.
            print("Received '{}' from client".format(in_data))

            # Process the received data and send something back to the client.
            out_data = in_data[::-1]
            print("Sending '{}' back to the client".format(out_data))
            connection.sendall(out_data.encode())       # Send data.

        # Make sure the connection is closed securely.
        finally:
            connection.close()
            print("Closing connection from {}".format(client_address))

def mirror_client(server_address=("0.0.0.0", 33333)):
    """A client program for mirror_server()."""
    print("Attempting to connect to server at {}...".format(server_address))

    # Set up the socket to be the same type as the server.
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(server_address)    # Attempt to connect to the server.
    print("Connected!")

    # Send some data from the client user to the server.
    out_data = input("Type a message to send: ")
    client_sock.sendall(out_data.encode())              # Send data.

    # Wait to receive a response back from the server.
    in_data = client_sock.recv(1024).decode()           # Receive data.
    print("Received '{}' from the server".format(in_data))

    # Close the client socket.
    client_sock.close()



def tic_tac_toe_server(server_address=("0.0.0.0", 44444)):
    """A server for playing tic-tac-toe with random moves."""
    # Specify the socket type, which determines how clients will connect.
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(server_address)
    server_sock.listen(10)
        # Wait for a client to connect to the server.
    print('\nWaiting for a connection...')
    connection, client_address = server_sock.accept()
    isRunning = True
    i=0
    while isRunning:
        try:
            # Receive data from the client.
            in_bytes = connection.recv(1024).decode()
            in_game = json.loads(in_bytes, object_hook=tic_tac_toe_decoder)
            i+=1
            # Process the received data and send something back to the client.
              
            #get all of the coordinates that haven't been filled yet
            coordinates=[]
            for i in range(3):
                for j in range(3):
                    if in_game.board[i][j] == ' ':
                        coordinates.append((i,j))     
            
            if in_game.winner is not None:
                connection.sendall("WIN".encode())
                isRunning = False
            elif len(coordinates)==0:
                connection.sendall("DRAW".encode())
                isRunning = False
            else:
            #choose one of them randomly
                i = random.randint(0,len(coordinates)-1)
                choice = coordinates[i]
                in_game.move(choice[0],choice[1])#move. If I lose it'll throw an error
                if in_game.winner is not None:
                    raise ValueError()
                connection.sendall(json.dumps(in_game,cls=TicTacToeEncoder).encode() )# Send data.
        except ValueError:
            connection.sendall("LOSE".encode())
            connection.sendall(json.dumps(in_game,cls=TicTacToeEncoder).encode() )# Send data.
            isRunning = False
            
    connection.close()
            #end with closing the connection no matter what


def tic_tac_toe_client(server_address=("0.0.0.0", 44444)):
    """A client program for tic_tac_toe_server()."""
    print("Attempting to connect to server at {}...".format(server_address))

    # Set up the socket to be the same type as the server.
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(server_address)    # Attempt to connect to the server.
    print("Connected!")

    # Send some data from the client user to the server.
    game = TicTacToe()
    #keep prompting while we're still playing the game
    while True:
        print(game)
        game = runGame(game,client_sock)
        if game is None:
            break
        
    # Close the client socket.
    client_sock.close()
    
    
def askInputCoords(game):
    #prompt for row & keep prompting if it's a bad input or if they can't make a move in that row
    player_move_x = input("Make a move by entering in the row number (starting with 0)\n")
    while player_move_x not in ['0','1','2'] or sum([x==' ' for x in game.board[int(player_move_x)]])==0:
        sys.stdout.flush()
        print("Invalid choice! Try again.")
        player_move_x = input("Make a move by entering in the row number (starting with 0)\n")
    player_move_x = int(player_move_x)
     #prompt for column & keep prompting if it's a bad input or they can't move there        
    player_move_y = input("Make a move by entering in the column number (starting with 0)\n")
    while player_move_y not in ['0','1','2'] or game.board[player_move_x][int(player_move_y)]!=' ':
        sys.stdout.flush()
        print("Invalid choice! Try again.")
        player_move_y = input("Make a move by entering in the column number (starting with 0)\n")
    player_move_y = int(player_move_y)
    return player_move_x,player_move_y
    
def runGame(game,client_sock):    
    coords = askInputCoords(game)        
#looks like it all checked out, so make the move and send the data up to the server            
    game.move(coords[0],coords[1])
    
    #encode it into bytes and send it
    encodedGame = json.dumps(game,cls=TicTacToeEncoder).encode()
    client_sock.sendall(encodedGame)              # Send data.
    # Wait to receive a response back from the server.
    in_data = client_sock.recv(1024).decode()           # Receive data.
    try:
        game = json.loads(in_data,object_hook=tic_tac_toe_decoder) 
    except:
        if in_data == 'LOSE':
            print('You Lost!')
            board = json.loads(client_sock.recv(1024).decode(),object_hook=tic_tac_toe_decoder)  # Receive board data.
            print(board)
        elif in_data == 'WIN':
            print("You Won!!")
        else:
            print("Draw!")  
        return None  
    return game    
    