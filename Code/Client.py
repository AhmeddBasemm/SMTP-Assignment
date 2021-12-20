'''
This is the Client side  python script.

Features:
-Connects to SMTP Server created with Server.py.
-Has a GUI (Graphical User Interface).
-Command Line Console to print current operation and info.

Please Check the Server.py & Read.me file too.
Ahmed Basem Ahmed Alsaeed Ali.
TKH ID# 202000188.
'''
#-------------------------------------------------------------------------------------
#importing Libraries
from socket import * #Socket Programming Library
from Utils import * #Custom Library for redundant functions
import tkinter as tk   #GUI Library
from tkinter.ttk import * #Exetntion to tk Library
import atexit,sys,os #Libraries for registering atexit functions and system functions

#Server Settings Variables
ResponseSize = 1024 #Received message standard size
connected = False #Connection status variable
#-------------------------------------------------------------------------------------
# function to validate digit entry
def only_numbers(char):
    return char.isdigit()
#Gui Initiation
def NewEmailWindow():
    #Global Variable Refrences
    global eData,ServerIP,ServerPort,From,To,Subject,root,Connectionbtn

    #Intializing the Window
    root =tk.Tk()

    #Color variables
    bgc = 'light grey'
    LblFG = "black"
    entryFG = "blue"
    
    #Window Configuration
    root.title("New Email") #Title
    root.configure(bg=bgc)  #Background Color
    root.grid_rowconfigure(6, weight=1) #Grid row weight distribution
    root.grid_columnconfigure(1, weight=1) #Grid column witgh distribution

    #Setting String Variables to Store user entry
    ServerIP = tk.StringVar(root) #Stores Server IP address
    ServerPort = tk.StringVar(root) #Stores Server port number
    From =tk.StringVar(root) #Stores mail from input 
    To = tk.StringVar(root) #Stores mail to input
    Subject = tk.StringVar(root) #Stores subject input

    #Validation variable to register the validation Function for the port entry
    validation = root.register(only_numbers)

    #IP Label & Entry setup
    lIP = Label(root, text="Server IP:", background=bgc, foreground=LblFG)
    eIP = Entry(root,textvariable = ServerIP, foreground=entryFG)

    #Port number Label & Entry setup
    lPort = Label(root, text="Server port:", background=bgc, foreground=LblFG)
    ePort = Entry(root,textvariable = ServerPort,foreground=entryFG,validate="key", validatecommand=(validation, '%S'))
    
    #Mail From Label & Entry setup
    lFrom = Label(root, text="From:", background=bgc, foreground=LblFG)
    eFrom = Entry(root,textvariable = From,foreground=entryFG,)

    #Mail To Label & Entry setup
    lTo = Label(root, text="To:", background=bgc, foreground=LblFG)
    eTo = Entry(root,textvariable = To,foreground=entryFG)

    #Subject Label & Entry setup
    lSubject = Label(root, text="Subject:", background=bgc, foreground=LblFG)
    eSubject = Entry(root,textvariable = Subject,foreground=entryFG)

    #Message Label & Tett-box setup
    lData = Label(root, text="Message:", background=bgc, foreground=LblFG)
    eData = tk.Text(root,height= 10, width=50,foreground=entryFG)
    eData.grid(row = 6, column = 0, sticky = tk.NSEW, pady = 3,columnspan=2,padx=1)

    #Send button setup
    SendBtn = tk.Button(root, text='Send', foreground='White', background= 'dark green', height = 1, width = 10,command=PopulateEmail)
    SendBtn.grid(row = 7, column = 0, pady = 3,)
    
    #Connect/Quit Toggle setup
    Connectionbtn = tk.Button(root, text='Connect', foreground='White', background= 'dark green', height = 1, width = 10,command=connectionToServer)
    Connectionbtn.grid(row = 7, column = 1, sticky = tk.W, pady = 3,)

    #Lists to Store lbl variable names
    Lbls = ['lIP','lPort','lFrom','lTo','lSubject','lData'] 
    #List to Store Entry variable names
    Entrys = ['eIP','ePort','eFrom','eTo','eSubject']

    #Loop through labels and assign them to row i column 0
    i = 0
    for item in Lbls:
        eval(item).grid(row = i, column = 0, sticky = tk.EW, pady = 2)
        i += 1

    #Loop through labels and assign them to row i column 1
    i = 0
    for item2 in Entrys:
        eval(item2).grid(row = i, column = 1, sticky = tk.EW, pady = 3,padx=1,)
        i += 1
    
    #Register onCloseWindow Function to be called when GUI is closed
    root.protocol("WM_DELETE_WINDOW", onCloseWindow)
    #Run the GUI mainloop and display its elements
    root.mainloop()
#Function called on GUI close event
def onCloseWindow():
    #tries to disconnect and exit
    try:
        Disconnect()
        sys.exit()
    except:
        #on faliure to disconnect it exits the program
        sys.exit()
#Function to get the email info from the GUI
def PopulateEmail():
    #Global Variable Refrences
    global eData,eFrom,eTo,eSubject

    #Check if connected
    if connected:    
        #Grabs lines from the GUI message Text-Box
        DATA = eData.get(1.0,"end")
        #Check if there are any lines
        if len(DATA) > 1:
            #Splits and stores lines in a list
            DATA = DATA.split("\n")
            #Remove any empty lines at the end of message
            while DATA[len(DATA)-1] == "":
                DATA.pop(len(DATA)-1)

            #Add the Data ending statment to the lines
            DATA.extend([".",""])
        else:
            #Fills the DATA variable with the Ending Statment
            DATA = [".",""]
        #-------------------------------------------------------------------------------------
        #Grabs the User input from the GUI and pass them to the SendEmail function         
        SendEmail(Server,From.get(),To.get(),Subject.get(),DATA)
#Function for the connect button
def connectionToServer():
    #Global Variable Refrences    
    global Server,connected,Connectionbtn

    #Check Connection state
    if not connected:
        #Grabs the IP and Port Number from the GUI
        #Create Socket using the ConnectToServer Function
        Server = ConnectToServer(ServerIP.get(),int(ServerPort.get()))
    else:
        #Calls the Disconnect Function
        Disconnect()
#-------------------------------------------------------------------------------------
#Function to connect to the server 
def ConnectToServer(ip,Serverport):
    #Global Variable Refrences
    global connected,Connectionbtn
    #Try to connect to Server
    try:
        print("Client Application is running")
        print("os Proccess ID", os.getpid())
        #Setup Socket Address Family and TCP

        s = socket.socket(AF_INET,SOCK_STREAM)
        print("TCP Socket Created")
        print("File Descriptor assinged by OS:",s.fileno())
        
        print("My addrress:",getip())
        #Connecting to the Server Socket
        s.connect((ip,Serverport))
        print("Connected to Server: {0}:{1}".format(ip,Serverport)) 

        #Set connected status to True
        connected = True
        #Receive and check connection status code 220
        ReceiveResp(s,"220")
        
        #Receive Server extracted info 
        Response = s.recv(ResponseSize).decode("utf-8")
        print("-->",Response)

        #Sending HELO message
        message = 'HELO'
        s.send(message.encode())
        print("HELO Message Sent!")

        #Receive and check connection status code 250    
        ReceiveResp(s,"250")
        #Set connection button color to red and text to Quit in the GUI
        Connectionbtn.configure(background="dark red",text="Quit")
        
        #return the socket object
        return s
    except:
        #print Failure Status
        print("Couldnt Connect To Server: {0}:{1}".format(ip,Serverport)) 
        #set connected boolean to false
        connected = False
#Function To send Email  
def SendEmail(s,From,To,Subject,Data):
    #Global Variable Refrences
    global SequenceNumber,root
    #Check if connected
    if connected:
        #Mail From Command
        while True:
            #Send Mail From Command including the user input from the GUI
            message = "MAIL FROM: <{}>".format(From)
            s.send(message.encode())
            
            #Receive and check connection status code 250  
            if ReceiveResp(s,"250"):
                #break out of the loop
                break
            else:
                #Print Invalid Email status and Disconnect from the server
                print("Invalid Email")
                Disconnect()
                break

        # Input email recipients separated by comma and space (, )
        while True:
            #Split and Store the recepient emails 
            tos = To.split(", ")
            #reset counter
            validEmails = 0
            
            #Loop through the email list
            for to in tos:
                #Send RCPT TO command including the user input from the GUI
                message = "RCPT TO: <{}>".format(to)
                s.send(message.encode())

                #Receive and check connection status code 250  
                if ReceiveResp(s,"250"):
                    validEmails += 1
                else:
                    print("Invalid Email")
                    

            #Break while loop when all emails are verified        
            if validEmails == len(tos):
                break
            else:
                #Print Invalid Email status and Disconnect from the server
                print('One or more email addresses are invalid. Please re-enter')
                Disconnect()
                break
               
        #Send DATA Command 
        s.send("DATA".encode())

        #Receive and check connection status code 354  
        if ReceiveResp(s,"354"):
            #Send user input subject entry
            s.send("Subject:{}".format(Subject).encode())
            print("Message:")
            
            #Loop through the message lines
            for data in Data:
                #Send each line to the server
                s.send(data.encode())
                print(data)

                #Receive and check connection status code 250 to stop sending lines 
                Response = s.recv(1024).decode("utf-8")
                if Response.find("250") >-1:
                    print("Email Sent!")
                    break
#Function to diconect from server
def Disconnect():
    #Global Variable Refrences
    global connected,Server
    #Check if connected
    if connected:
        #Send Quit command
        Server.send("QUIT".encode())

        #Receive and check connection status code 221
        if ReceiveResp(Server,"221"):
            print("Disconnected")
              
            Server.close() #Close server socket
            connected = False #Set connected bool to false
            root.destroy() #Destroy current gui window
#Registering the Disconnect function to run on program Exit
atexit.register(Disconnect)
#While Loop to keep the client running
while True:
    #Intializing A blank NewEmailWindow       
    NewEmailWindow()
#-------------------------------------------------------------------------------------
