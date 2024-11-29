
import streamlit as st
import detect_or_track as dt
import detect_or_track2 as dt2
import argparse
import yaml
import sys
import sqlite3
from PIL import Image
import pandas as pd
import os
import time

if sys.version_info>=(3,0):
    from queue import Queue

else:
    from Queue import Queue

parser = argparse.ArgumentParser()
parser.add_argument(
    "-s",
    "--source-config-file",
    default="./config.yaml",
    help="Input your config.yaml file",
)
value_parser = parser.parse_args()

with open(value_parser.source_config_file, "r") as f:
    file_config = yaml.safe_load(f)




def streamApp():
    st.set_page_config(page_title="Multiple Camera Frames", page_icon=":guardsman:", layout="wide")
    cams = []
    check_socket = st.sidebar.checkbox("Start receiving video from client")
    check1 = st.sidebar.checkbox("Cam1")
    if check1 and not check_socket:
        user_input1 = st.sidebar.text_input("Please enter IP address for Cam1", value = 0)

    check2 = st.sidebar.checkbox("Cam2")
    if check2 and not check_socket:
        user_input2 = st.sidebar.text_input("Please enter IP address for Cam2", value = 1)
    
    
    def create_connection(db_file):
        """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Exception as e:
            st.write(e)

        return conn
    
    def create_database():
        st.markdown("# Create Database")

        st.info("""A database in SQLite is just a file on same server. 
        By convention their names always must end in .db""")


        db_filename = st.text_input("Database Name")
        create_db = st.button('Create Database')
        
        conn = create_connection('example.db')
        mycur = conn.cursor() 
        mycur.execute("PRAGMA database_list;")
        available_table=(mycur.fetchall())
        with st.expander("Available Databases"): st.write(pd.DataFrame(available_table))
        
        if create_db:
            
            
            if db_filename.endswith('.db'):
                conn = create_connection(db_filename)

                st.success("New Database has been Created! Please move on to next tab for loading data into Table.")
            else: 
                st.error('Database name must end with .db as we are using sqlite in the background to create files.')


    def upload_data():
        st.markdown("# Upload Data")
        sqlite_dbs = [file for file in os.listdir('.') if file.endswith('.db')]
        db_filename = st.selectbox('Database', sqlite_dbs)
        table_name = st.text_input('Table Name to Insert')
        conn = create_connection(db_filename)
        uploaded_file = st.file_uploader('Choose a file')
        upload = st.button("Create Table")
        if upload:
            #read csv
            try:
                df = pd.read_csv(uploaded_file, index_col = "Index")
                df.to_sql(name=table_name, con=conn)
                st.write('Data uploaded successfully. These are the first 5 rows.')
                st.dataframe(df.head(5))

            except Exception as e:
                st.write(e)

    # Initialize session state
    intro, db, tbl, qry = st.tabs(["1 Surveillance","2 Add Criminal Details", "3 Create Database", "4 Upload Data"])
    with intro:
      
        # Display details of page 1
        
        st.title("Multiple Camera Frames")
        imgs = []
        # Capture video streams
        # cap1 = cv2.VideoCapture(0)
        # cap2 = cv2.VideoCapture(1)
        
        col1, col2 = st.columns(2)
        with col1:
            img1 = st.empty()
            imgs.append(img1)
            
        with col2:
            img2 = st.empty()
            imgs.append(img2)
            
            
        # Continuously read frames
        st.write("Face Recognized")
        col3, col4 = st.columns(2)
        with col3:
            img3 = st.empty()
            
        with col4:
            streamTable = st.empty()

        if st.button('Start'):
            if check1 or check2:
                cams.append(user_input1)
                cams.append(user_input2)
                SHOW_MAIN = False
                st.write('In progress...')
                with open('streams.txt', 'w') as f:
                    for i in cams:
                        f.write(i)
                        f.write("\n")
                dt.run(imgs, img3, streamTable, "streams.txt")
        
            if check_socket:
                dt2.run(imgs, img3, streamTable, 'output_image.jpg')
                

        # Define function to exit program
        def stop_inference():
            sys.exit()

        # Add a stop button to the Streamlit app
        if st.button("Stop Inference"):
            stop_inference()

    
            
  
    with db:
        # Display details of page 2
        st.title("Add Criminal Details")

        col1, col2 = st.columns(2)
        with col1:
            uploaded_files = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
            
        with col2:
            name = st.text_input("Name")
            crime = st.text_input("Crime")
            
        if st.button('Submit'):
            st.write('In progress...')
            
            conn = sqlite3.connect('example.db')
            c = conn.cursor()
            # (id INTEGER PRIMARY KEY, image BLOB)
            c.execute('''CREATE TABLE IF NOT EXISTS criminals
                        (name text, type_of_crime text, image blob)''')

            for uploaded_file in uploaded_files:
                file_contents = uploaded_file.read()
                c.execute("INSERT INTO criminals (name, type_of_crime, image) VALUES (?, ?, ?)", (name, crime, file_contents))
                conn.commit()
                image = Image.open(uploaded_file)
                rgb_im = image.convert('RGB')

                folder_path = f"data/knownfaces/{name}"

                if not os.path.isdir(folder_path):
                    os.makedirs(folder_path)
                
                rgb_im.save(f"{folder_path}/image{time.time()}.jpg")
            conn.close()
            st.success("New details are saved successfully!")
            st.experimental_rerun()
        
    with tbl:
        create_database()
    with qry:
        upload_data()
    #     dt.run(img1, img3, streamTable, "0")
    # if st.button('Start Cam2'):
    #     st.write('You clicked the button!')
    #     dt.run(img2, img3, streamTable, "1")

    # Display frames
        
    # Create two camera inputs
    # cam1 = st.camera_input(label = "Cam1")
    # cam2 = st.camera_input(label = "Cam2")


if __name__ == "__main__":
    streamApp()