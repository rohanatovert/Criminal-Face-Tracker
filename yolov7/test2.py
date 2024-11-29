# import streamlit as st
# import threading
# from streamlit.scriptrunner import add_script_run_ctx

# stSystemStatsPlaceHolder = None

# def update_system_stats():
#         global stSystemStatsPlaceHolder
#         with stSystemStatsPlaceHolder:    
#               col1, col2, col3, col4, col5 = st.columns(5)

#               col1.metric("Memory", '1')
#               col2.metric("Swap", '2')
#               col3.metric("CPU", '3')
#               col4.metric("CPU Temp", '4')
#               col5 .metric("GPU Temp", '5')


# stSystemStatsPlaceHolder = st.empty()

# thread = threading.Thread(target=update_system_stats)
# add_script_run_ctx(thread)
# thread.start()



import streamlit as st
import numpy as np
# Global variable to store the frames

import socket_data
imgs = []


# Streamlit app
def streamlit_app():
    st.title('Video Stream')
    s1 = st.empty()
    imgs.append(s1)
    socket_data.receive_data(imgs)
    
    
    
    # Add any additional Streamlit app code here

if __name__ == '__main__':
    streamlit_app()