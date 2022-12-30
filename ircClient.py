#!/usr/local/bin/python3
# -*- coding: utf-8 -*-


import socket       # Import socket module in order to create socket instances and handle connections
import threading
import time    # Import threading module in order to create threads and handle multiple connections
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTextEdit, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton
import sys        # Import sys module in order to handle system arguments   

# Global variables
name = ''
password = ''

# SERVER_ADDRESS = '127.0.0.1'                              # test server
SERVER_ADDRESS = 'ec2-3-94-9-109.compute-1.amazonaws.com'   # prod server
SERVER_PORT = 80                                            # listen port

''' Initiate client and connect to server '''
socket_instance = socket.socket()
socket_instance.connect((SERVER_ADDRESS, SERVER_PORT))


class LoginWindow(QWidget):
    
    
    def __init__(self):
        super().__init__()

        # Create the GUI widgets
        self.setWindowTitle("Client")
        self.login_label = QLabel("LOGIN", self)
        self.username_line_edit = QLineEdit(self)
        self.username_line_edit.setPlaceholderText("Username: ")
        
        self.password_line_edit = QLineEdit(self)
        self.password_line_edit.setEchoMode(QLineEdit.Password)
        self.password_line_edit.setPlaceholderText("Password: ")
        self.login_button = QPushButton("Login", self)
        
        # Set up the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.login_label)
        layout.addWidget(self.username_line_edit)
        layout.addWidget(self.password_line_edit)
        layout.addWidget(self.login_button)
        
        # Connect the login button to the login function
        self.login_button.clicked.connect(self.login)
        
        
    def login(self):
        ''' Login to server '''
        # Send username to server
        response = socket_instance.recv(2048)
        name = self.username_line_edit.text()
        socket_instance.send(str.encode(name))
        response = socket_instance.recv(2048)
        password = self.username_line_edit.text()	
        socket_instance.send(str.encode(password))
        
        response = socket_instance.recv(2048).decode()
        print('Response from server:', response)
        
        ''' 
        R : Status of Connection     :
	    1 : Registeration successful :
	    2 : Connection Successful    :
	    3 : Login Failed             :
        '''
        
        if response != 3:
            self.close()                # close LoginWindow
            time.sleep(1)               # wait for 1 second
            chat_window = ChatWindow()  # create ChatWindow
            chat_window.show()          # show ChatWindow
        else:
            self.close()                # close LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()    # show again
            print('Username or password is incorrect. Please try again.')
  
# inherit from QWidget and LoginWindow class to get socket_instance
class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Create the GUI widgets
        self.setWindowTitle("Client Chat Window")
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.line_edit = QLineEdit(self)
        self.send_button = QPushButton("Send", self)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.text_edit)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.line_edit)
        h_layout.addWidget(self.send_button)
        layout.addLayout(h_layout)

        # Connect the send button to the send_message function
        self.send_button.clicked.connect(self.send_message)
        
        # Print connection information and wait for user's input to send to server
        print('\nConnected to Server! \nServer IP:', SERVER_ADDRESS, '\nServer PORT:', SERVER_PORT)
        print('\nSockname: ', socket_instance.getsockname()[0], '\nClient PORT:', socket_instance.getsockname()[1])
        print('\nPeername: ', socket_instance.getpeername()[0], '\nServer PORT:', socket_instance.getpeername()[1])
        
        # Create the send and receive threads
        self.send_thread = threading.Thread(target=self.send_message)
        self.receive_thread = threading.Thread(target=self.receive_message)

        # Start the send and receive threads
        self.send_thread.start()
        self.receive_thread.start()
        

    def send_message(self):
        ''' Send message to server '''
        msg = self.line_edit.text()
        self.line_edit.clear()
        socket_instance.send(msg.encode()) # Parse message to utf-8 and send to server
         
         
    def receive_message(self):
        ''' Receive messages sent by the server and display them to user '''
        print('\nWaiting from server...\n')
        while True: # Keep receiving messages
            try: # Try to receive message from server and print it to user
                msg = socket_instance.recv(1024) # parse it to utf-8 format (bytes)
                if msg: # If there is a message, print it to user
                    print('Message from: ', msg.decode('utf-8')) # Print message to user
                    self.text_edit.append(msg.decode('utf-8'))
                else: # If there is no message, close connection
                    socket_instance.close() # Close connection
                    break # Break loop in order to stop receiving messages from server

            except Exception as e: # If there is an error, print it and close connection
                print(f'Error handling message from server: {e}')
                self.text_edit.append(f'Error handling message from server: {e}')
                socket_instance.close() # Close connection
                break # Break loop in order to stop receiving messages from server


    
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    # window = ChatWindow()
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())