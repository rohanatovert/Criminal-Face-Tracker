# import socket
# import cv2
# import numpy as np

# # Create a socket object
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# # Get local machine name
# host = socket.gethostname()
# port = 8501

# # Bind the socket to a public host and a port
# server_socket.bind((host, port))

# # Listen for incoming connections
# server_socket.listen(5)

# print('Server listening on {}:{}'.format(host, port))

# while True:
#     # Wait for a connection
#     client_socket, addr = server_socket.accept()

#     print('Client connected from {}:{}'.format(addr[0], addr[1]))

#     # Receive data from client
#     data = b''
#     while True:
#         img_len = 175428 # received by sender.py
#         e=0
#         data = ''
#         while e < img_len:
#             packet = client_socket.recv(1024)
#             e += len(packet)
#             data += str(packet)
#             # Receive data from the server
#             # packet = client_socket.recv(4096)
#             if not packet:
#                 break
#             # data += packet
        
#         # Check if the current batch of data contains a complete frame
#         frame_start = data.find(b'\xff\xd8')
#         frame_end = data.find(b'\xff\xd9')
#         if len(data) > 4 and frame_start != -1 and frame_end != -1:
#             # Convert the data to a numpy array
#             img_array = np.frombuffer(data, np.uint8)
            
#             # Decode the numpy array into an OpenCV image
#             img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
#             print(img_array)
#             # Show the image
#             cv2.imshow('Client Feed', img)
            
#             # Reset the buffer
#             data = b''
        
#         # Exit on 'q' key press
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break






# # Cleanup
# cv2.destroyAllWindows()
# client_socket.close()
# server_socket.close()


# # import libraries
# from vidgear.gears import NetGear
# import cv2

# # define various tweak flags
# options = {'-rtsp_transport':'http'}

# # Define Netgear Client at given IP address and define parameters 
# # !!! change following IP address '192.168.x.xxx' with yours !!!
# client = NetGear(
#     address="20.207.207.133",
#     port="8501",
#     protocol="tcp",
#     pattern=1,
#     receive_mode=True,
#     logging=True,
#     **options
# )
# # infinite loop
# while True:
#     # receive frames from network
#     frame = client.recv()

#     # check if frame is None
#     if frame is None:
#         #if True break the infinite loop
#         break

#     # do something with frame here

#     # Show output window
#     cv2.imshow("Output Frame", frame)

#     key = cv2.waitKey(1) & 0xFF
#     # check for 'q' key-press
#     if key == ord("q"):
#         #if 'q' key-pressed break out
#         break

# # close output window
# cv2.destroyAllWindows()
# # safely close client
# client.close()





import socket, cv2, pickle,struct

# Socket Create
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_name  = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print('HOST IP:',host_ip)
port = 8501
socket_address = (host_ip,port)

# Socket Bind
server_socket.bind(socket_address)

# Socket Listen
server_socket.listen(5)
print("LISTENING AT:",socket_address)


# Socket Accept
while True:
    client_socket,addr = server_socket.accept()
    print('GOT CONNECTION FROM:',addr)
    if client_socket:
        data = b""
        payload_size = struct.calcsize("Q")
        while True:
            while len(data) < payload_size:
                packet = client_socket.recv(4*1024) # 4K
                if not packet: break
                data+=packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q",packed_msg_size)[0]
            
            while len(data) < msg_size:
                data += client_socket.recv(4*1024)
            frame_data = data[:msg_size]
            data  = data[msg_size:]
            frame = pickle.loads(frame_data)
            cv2.imshow("RECEIVING VIDEO",frame)
            key = cv2.waitKey(1) & 0xFF
            if key  == ord('q'):
                break


    