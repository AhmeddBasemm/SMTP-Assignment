'''
This a file for redundant functions.
Please Check Client.py, Server.py & Read.me file too.

Note:
CreateFirewall Function is not implemented as it requires admin privledges

Ahmed Basem Ahmed Alsaeed Ali.
TKH ID# 202000188.
'''
#-------------------------------------------------------------------------------------
import socket,os
#-------------------------------------------------------------------------------------
#Function for Retrieving the device NIC IP address 
def getip():
    #Get Ip using getHostbyname function
    ip = socket.gethostbyname(socket.gethostname())
    return ip
#Function for receiving TCP status codes and Checking them 
def ReceiveResp(Socket,code):
    #Receiving responsed status code
    Response = Socket.recv(1024).decode("utf-8")
    #Check if code matches
    if Response.find(code) == -1:
        print(code,"Message Not Recieved!")
        print("--> Error", Response)
        #return operation outcome status
        return False
    else:
        print("-->",Response)
        #return operation outcome status
        return True
#-------------------------------------------------------------------------------------
#Requires Admin Previlidges
#Function For Creating Firewall Rules
def CreateFirewallRule(portin,portout):
    #Using netsh (net Shell) we allow tcp communication on certain ports
    #Inbound
    os.popen('netsh advfirewall firewall add rule name="AllowMySMTPIn" dir=in action=allow protocol=TCP localport={1}'.format(portin))
    #Outbound
    os.popen('netsh advfirewall firewall add rule name="AllowMySMTPOut" dir=out action=allow protocol=TCP localport={1}'.format(portout))

