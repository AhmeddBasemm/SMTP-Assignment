'''
This is the Server side python script.

Features:
-Hosts an SMTP server.
-Accepts client Connections and extracts network information.
-Command line console to print current operation and info.
-Receives "Mail FROM: <..>","RCPT TO: <..>","DATA" and "QUIT" commands.
-Saves emails in seperate folders by hour & text files using Mail from addresses.

Please check the Client.py & Read.me file too.
Ahmed Basem Ahmed Alsaeed Ali
TKH ID# 202000188
'''
#-------------------------------------------------------------------------------------
#importing Libraries
from socket import * #Socket Programming Library
from Utils import * #Custom Library for redundant functions
from datetime import datetime #Date and Time Library
import os,sys,re,atexit #Additonal Libraries for string matching, system functions and information access
#-------------------------------------------------------------------------
#Email info variables
From = "" 
ToList = "" 
Subject = "" 
Data = "" 
EmailCount = 0 #Email Counter

#-------------------------------------------------------------------------
#Server Settings Variables
ServerIP = getip() #Server socket IP address
ServerPort = 25 #Server port number
Backlog = 1 #Backlog queue limit
ResponseSize = 1024 #Received message standard size
ReceivingCommand = False #Determines whether server is receiving commands or not
Online = False #Server status variable
SequenceNumber = 0 #Variable to track the command Sequence
path = "Emails "+ datetime.now().strftime("%Y-%m-%d, %I %p") #Folder name using date and time for classification

#-------------------------------------------------------------------------
#Setup a socket to listen to client connection requests
if not Online:
    try:
        print("Server Application is running")
        print("os Proccess ID", os.getpid())
        #Setup Socket Address Family and TCP
        ServerSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        #Allow program to use a socket already in use
        ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("TCP Socket Created")
        print("File Descriptor assinged by OS:",ServerSocket.fileno())
        
        #Bind Server Socket to a defined IP Address and Port
        ServerSocket.bind((ServerIP,ServerPort))
        
        #Start Listening to Clients
        ServerSocket.listen(Backlog)
        print("\nServer is online\nListening on IP Address: {0}, Port: {1}".format(ServerIP,ServerPort))
        #Set Online Status to True 
        Online = True
    except:
        #Set Online Status to False
        Online = False
        print("Socket cant be created on IP Address: {0} and Port: {1}!".format(ServerIP,ServerPort))
        input("Please Make Sure Socket is not in use and Re-run")

#Function to reset email info variables to default
def defaults():
    #Global Variable Refrences    
    global From,ToList,Subject,Data,SequenceNumber,EmailCount
    #Email info variables
    From = ""
    ToList = ""
    Subject = ""
    Data = ""
    SequenceNumber = 0
    EmailCount = 0      

#Function to Get a Mac address that corresponds to an ip from the Arp table
def GetMac(ip):
    #Grab the arp table from the cmd prompt using arp -a command
    with os.popen("arp -a") as f:
        data = f.read()
    
    #Look up the ip and find the start of the corresponding mac address     
    start = data.rfind(ip)+len(ip)+7
    end = start+17
    mac = data[start:end]
    #Return the mac address
    return mac
#-------------------------------------------------------------------------
#Function to Save the received emails
def SaveEmail():
    #Global Variable Refrences
    global EmailCount,path
    #Open a new text file with using the from address as the name
    with open(sys.path[0]+"\\"+path+"\{}.txt".format(From),"a") as f:
        #Write a divider
        f.write("-"*50+"\n")
        #Write time and date of sending
        f.write("Sent @ "+ datetime.now().strftime("%Y-%m-%d %H.%M.%S")+"\n")
        #Save the email
        f.write("From: {0}\nTo: {1}\nSubject: {2}\nMessage:\n{3}".format(From,ToList[:len(ToList)-2],Subject,Data))
    #Increase Email Count
    EmailCount += 1 
    #Reset the email info variables to receive a new email
    defaults()
#Function to be executed on exit
def onexit():
    #Close the Server Listening Socket if Online
    if Online:
        print("Closing Socket!")
        ServerSocket.close()
#Registering the onexit function to be executed before the program is closed
atexit.register(onexit)
#-------------------------------------------------------------------------
#For validating an email
def check(email):
    #Rules to govern the validty of the email
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # pass the regular expression
    # and the string into the fullmatch() method
    #To Check if the email is valid
    if(re.fullmatch(regex, email)):
        print("Valid Email")
        return (True,"None")
    else:
        print("Invalid Email")
        return (False,email)
#Function to execute instructions depending on the command
def Commander(ClientSocket,Command):
    #Global Variable Refrences    
    global From,ToList,Subject,Data,SequenceNumber,ReceivingCommand
    #Mail From <..> Command
    if Command.find("MAIL FROM") > -1 and SequenceNumber == 0:
        #Extracting the email from the command by removing the command and <> tags
        FromMail = Command.strip("MAIL FROM: <")
        FromMail = FromMail.strip(">")
        #Calling utils.check function to check if email is valid
        valid,err = check(FromMail)
        if valid:
            #Reset the email info variables to receive a new email
            defaults()
            #Reply to the client with a 250 status code
            ClientSocket.send('250 OK'.encode())
            #Increase Sequence number by 1
            SequenceNumber += 1
            #Set the From variable to the extracted email
            From = FromMail
        else:
            #Send an error message to the Client
            ClientSocket.send(err.encode())       
    #RCPT TO <..> Command
    elif Command.find("RCPT TO") > -1:
        #Extracting the email to the command by removing the command and <> tags        
        ToMail = Command.strip("RCPT TO: <")
        ToMail = ToMail.strip(">")
        #Calling utils.check function to check if email is valid
        valid,err = check(ToMail)
        if valid:
            #Reply to the client with a 250 status code
            ClientSocket.send('250 OK'.encode())
            #Add the address to the To list
            ToList += ToMail+", "
        else:
            #Send an error message to the Client
            ClientSocket.send(err.encode())
    #DATA Command
    elif Command.find("DATA") > -1:
        #Reply to the client with a 354 status code
        ClientSocket.send('354 OK'.encode())
        #Start a while true loop to receive data untill a "."
        while True:
            #Receive and print the data from the client
            data =  ClientSocket.recv(1024).decode("utf-8")
            print(data)
            #Check for the Subject Feild and extract the Subject
            if data[:7] == "Subject":
                Subject = data[8:]
            else:
                #Store all other emal data in a variable with a newline in between
                Data += data + "\n"
            #Check for a "." item to end the data transmittion
            if data == ".":
                #Reply to the client with a 250 status code
                ClientSocket.send("250".encode())
                #call the Save Email Function
                SaveEmail()
                #Reset the Sequence Number to receive emails again and break
                SequenceNumber = 0
                print("message end")
                break
            else:
                #Reply to the client with a 0 status code to continue sending data
                ClientSocket.send("0".encode())
    #QUIT Command
    elif Command.find("QUIT") > -1:
        #Reply to the client with a 221 status code
        ClientSocket.send("221".encode())
        print("221 Sent")
        #Turn off the receiving command loop
        ReceivingCommand = False
        #Close the client socket properly and disconnect the client
        ClientSocket.close()
        print("Client Disconected")
    #Unkown Command
    else:
        #Reply to the client with a 503 error status code
        ClientSocket.send('503 Bad sequence of commands'.encode())
#-------------------------------------------------------------------------
#Start accepting client connections
while Online:
    #Accepting a client
    ClientSocket, addr = ServerSocket.accept()
    #Create a Folder to Store all emails at the current Hour
    try:
        os.mkdir(path)
        print("Directory '{}' Created".format(path))
    except:
        print("Directory '{}' Exists".format(path))

    #Construct a 220 Status code message to the client to initiate the Communication
    message = "220 Connection accepted from " + socket.gethostname()
    #Store and print the Client Information
    info = "Client Addr: "+addr[0] + " ,Mac Addr: "+ GetMac(addr[0]) + " ,Port:"+str(addr[1]) +"\n"
    print("\n"+ message)
    print(info)
    
    #Send the Status code and the client info back to the client 
    ClientSocket.send(message.encode())
    ClientSocket.send(info.encode())

    #Receive and Check HELO message From Client
    if ReceiveResp(ClientSocket,"HELO"):
        #Turn on the receiving command loop
        ReceivingCommand = True

    #send acknowledgment message to client with status code 250
    message = "250 Hello " + socket.gethostname() + '. Pleased to meet you.'
    ClientSocket.send(message.encode())
    #------------------------------------------------------------------------------------------------
    #While Loop to receive Commands
    while ReceivingCommand:
        #Receive command from client
        command = ClientSocket.recv(ResponseSize).decode("utf-8")
        #Pass the Command to the commander function
        Commander(ClientSocket,command)
    continue
