
### WORKS USING SOCKETS ##
# import socket, cv2, pickle,struct
# frames = []
# # Socket Create
# server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# host_name  = socket.gethostname()
# host_ip = socket.gethostbyname(host_name)
# print('HOST IP:',host_ip)
# port = 8501
# socket_address = (host_ip,port)
# import streamlit as st
# # Socket Bind
# server_socket.bind(socket_address)

# # live_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # live_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# # live_socket.connect(("localhost", 5005))

# # Socket Listen
# server_socket.listen(5)
# print("LISTENING AT:",socket_address)

# def receive_data(imgs):
#     # Socket Accept
#     while True:
#         client_socket,addr = server_socket.accept()
#         print('GOT CONNECTION FROM:',addr)
#         if client_socket:
#             data = b""
#             payload_size = struct.calcsize("Q")
#             while True:
#                 while len(data) < payload_size:
#                     packet = client_socket.recv(4*1024) # 4K
#                     if not packet: break
#                     data+=packet
#                 packed_msg_size = data[:payload_size]
#                 data = data[payload_size:]
#                 msg_size = struct.unpack("Q",packed_msg_size)[0]
                
#                 while len(data) < msg_size:
#                     data += client_socket.recv(4*1024)
#                 frame_data = data[:msg_size]
#                 data  = data[msg_size:]
#                 frame = pickle.loads(frame_data)

#                 # Example: Print frame shape
#                 frame = frame.reshape((480, 640, 3))
#                 # print('Received frame:', frame.shape)

#                 # Append the frame to the frames list
#                 frames.append(frame)
#                 # Display frames in real-time
#                 if frames:
#                     # Display the latest frame
#                     imgs[0].image(frames[-1], channels='BGR')

#                 print(frames)
                
                # live_socket.send("rtsp://localhost/live.sdp")
                # cv2.imshow("RECEIVING VIDEO",frame)
                # key = cv2.waitKey(1) & 0xFF
                # if key  == ord('q'):
                #     break


# if __name__ == '__main__':
#     receive_data()



##################################################################
import cv2
import zmq
import base64
import numpy as np
context = zmq.Context()
footage_socket = context.socket(zmq.SUB)
footage_socket.bind('tcp://*:8501')
footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))


def receive_data():
    while True:
        try:
            frame = footage_socket.recv_string()
            img = base64.b64decode(frame)
            npimg = np.fromstring(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)
            cv2.imwrite('output_image.jpg', source)
            
        except:
            pass

##############################################################