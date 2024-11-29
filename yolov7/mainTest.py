from multiprocessing import Process
from subprocess import Popen

# Start Streamlit app
def start_streamlit_app():
    streamlit_process = Popen(['streamlit', 'run', 'stream.py', '--server.port', '8502'])
    streamlit_process.wait()

# Start server
def start_server():
    import socket_data
    socket_data.receive_data()

if __name__ == '__main__':
    # Start Streamlit app process
    streamlit_process = Process(target=start_streamlit_app)
    streamlit_process.start()

    # Start server process
    server_process = Process(target=start_server)
    server_process.start()

    # Wait for both processes to finish
    streamlit_process.join()
    server_process.join()
