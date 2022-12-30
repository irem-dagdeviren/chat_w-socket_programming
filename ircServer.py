#!/usr/local/bin/python3
# -*- coding: utf-8 -*-


import socket     # Import socket module in order to create socket instances
import threading  # Import threading module in order to create threads
import hashlib    # Import hashlib module in order to hash password

connections = []  # Global variable that mantain client's connections
HashTable = {}    # Global variable that mantain client's username and password

# LISTENER_IP = '127.0.0.1'     # test server
LISTENER_IP = '172.31.90.138'   # prod server private
LISTENING_PORT = 80             # listen for connections


# Function : For each client connection, create a thread and handle the connection
def handle_user_connection(connection: socket.socket, address: str) -> None:
    ''' Handle user connection and receive messages sent by the user '''
    # Request Username
    connection.send(str.encode('LOGIN\n\nEnter username: ')) 
    name = connection.recv(2048) #kullanıcı adı alındı
    name = name.decode()
    # Request Password
    connection.send(str.encode('Enter password: ')) 
    password = connection.recv(2048)
    password = password.decode()
    # Password hash using SHA256
    password = hashlib.sha256(str.encode(password)).hexdigest() 
    
    # REGISTERATION PHASE   
    # If new user,  regiter in Hashtable Dictionary  
    if name not in HashTable:
        HashTable[name]=password
        connection.send(str.encode('Registeration Successful')) 
        print('Registered : ',name)
        print("{:<8} {:<20}".format('USER','PASSWORD'))
        for k, v in HashTable.items():
            label, num = k,v
            print("{:<8} {:<20}".format(label, num))
        print("-------------------------------------------")
        
    if name in HashTable:
        # If already existing user, check if the entered password is correct
        if(HashTable[name] == password):
            # Response Code for Connected Client 
            connection.send(str.encode('Connection Successful\n')) 
            print('Connected : ',name)
            # new !!
            broadcast(f'{name} has joined the chat', connection)
            # Add connection to connections list
            while True:  # Keep receiving messages
                try:     # Get client message
                    msg = connection.recv(2048)
                    if msg:
                        print(f'{address[0]}:{address[1]} - {msg.decode()}')
                        # Build message format and broadcast users connected on server
                        msg_to_send = f'{address[0]}:{address[1]} - {msg.decode()}'
                        broadcast(msg_to_send, connection)

                    else:  # Remove connection from connections list
                        remove_connection(connection)
                        break  # Break in order to stop receiving messages from client

                except Exception as e:
                    print(f'Error to handle user connection: {e}')
                    print(f'{address[0]}:{address[1]} - has left the chat')
                    remove_connection(connection)
                    break
            
        else:
            # Response code for login failed
            connection.send(str.encode('Login Failed')) 
            print('Connection denied : ',name)
    while True:
        break
    connection.close()


def broadcast(message: str, connection: socket.socket) -> None:
    ''' Broadcast message to all users connected to the server '''
    # print(f'\nBroadcasting message: {message}')
    for client_conn in connections:    # iterate on connections
        #if client_conn != connection:  # if it not the connection of who's send
            try:  # Try to send message to client connection
                client_conn.send(message.encode())
                # print(f'Broadcast: {client_conn.getpeername()}')

            except Exception as e:  # There is a chance of socket has died
                print(f'Error broadcasting message: {e}')
                remove_connection(client_conn)  # Remove


def remove_connection(conn: socket.socket) -> None:
    ''' Remove specified connection from connections list '''

    if conn in connections:  # Check if connection exists on connections list
        conn.close()  # Close socket connection
        connections.remove(conn)  # Remove connection from connections list


def server() -> None:
    ''' Start server and keep accepting connections '''
    # -> None means that this function doesn't return anything
    try:
        # Create server and specifying that it can only handle 4 connections
        socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_instance.bind((LISTENER_IP, LISTENING_PORT))  # Bind socket to port
        socket_instance.listen(4)  # Listen for connections and specify max
        print('Server is running...')
        print('IP:', socket_instance.getsockname()[0])
        print('PORT:', LISTENING_PORT)

        while True:  # Keep accepting connections
            socket_connection, address = socket_instance.accept()
            connections.append(socket_connection)  # Add client
            # Start a new thread to handle client connection
            # in order to send to others connections
            threading.Thread(target=handle_user_connection,
                             args=(socket_connection, address)).start()

    except Exception as e:  # If there is any problem, print error message
        print(f'An error has occurred when instancing socket: {e}')

    finally:  # In case of any problem we clean all connections
        if len(connections) > 0:  # if there is any connection
            for conn in connections:  # iterate on connections
                remove_connection(conn)  # remove connection
        socket_instance.close()  # close socket instance


if __name__ == "__main__":
    server()