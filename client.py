import socket
import struct
from threading import Thread
import time
import getch


Bold = "\033[1m"
Red = "\033[31;1m"
Green = "\033[32;1m"
Yellow = "\033[33;1m"
Blue = "\033[34;1m"
end = "\033[0;1m"


def startingThread(sock):
    try:
        endtime = time.time()+10
        while time.time() < endtime:
            try:
                sock.settimeout(max(0, endtime - time.time()))
                intosend = getch.getch()
                sock.sendall(intosend.encode())
            except:
                pass

    except:
        pass
    # print('\nfineshed this round')

def ScoreOutput(sock):
    try:
        endtime = time.time()+10
        while time.time() < endtime:
            output = sock.recv(1024)
            if output:
                print(output.decode('utf-8'))
    except Exception as e : print(e)

def Main():

    TEAM_NAME = f"{Yellow}Bugs Bunny\n{end}"
    print(f"{Green}Client started,listening for offer requests...\n{end}")
    client = UDPConn()
    try:
        client.bind(("", 13117))
    except:
        print(f"{Red}error binding{end}")

    while True:
        data1, addr = client.recvfrom(1024)
        host, UDP_Port = addr
        try:
            data1, data2 , TCP_Port = struct.unpack('!IBH', data1)
            if data1 == 0xfeedbeef and data2 == 0x2:  # checking recieved message from broadcast
                print(f"{Green}received offer from{end}", host, f"{Green},attempting to connect...\n{end}")
                sock = TCPConn(TCP_Port, host)
                try:
                    sock.sendall(TEAM_NAME.encode('utf-8'))
                    SendDataByThread(sock)
                    # ScoreOutput(sock)
                except:
                    print(f"{Red}server closed{end}")
                finally:
                    sock.close()
        except:
            pass



def TCPConn(TCP_Port, host):
    # TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, TCP_Port)
    try:
        sock.connect(server_address)
    except:
        print(f"{Red}connection failed{end}")
    return sock


def SendDataByThread(sock):
    DataIsFound = False
    endtime = time.time()+10
    while time.time() < endtime and not DataIsFound:
        data = sock.recv(1024)
        if data is not None:
            print(data.decode('utf-8'))
            # create the thread of sending
            thread = Thread(target=startingThread, args=(sock,))
            thread.start()
            thread.join()
            thread2 = Thread(target=ScoreOutput, args=(sock,))
            thread2.start()
            thread2.join()
            DataIsFound = True
        # else:
        #     DataIsFound = False


def UDPConn():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return client


if __name__ == '__main__':
    Main()