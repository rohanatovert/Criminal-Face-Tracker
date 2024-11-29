
import cv2
import face_recognition
import cv2
import os
import pickle
import streamlit as st
import pandas as pd
import sqlite3

conn = sqlite3.connect('example.db')
c = conn.cursor()



# Specify the parent directory where the folders of persons are stored
parent_dir = r"data\knownfaces"

# Create an empty dictionary to store face encodings for each person
face_encodings_dict = {}
crime_data = {}
c.execute('''CREATE TABLE IF NOT EXISTS criminals
                        (name text, type_of_crime text, image blob)''')

for person_dir in os.listdir(parent_dir):
    # Extract the person name from the folder name
    person_name = person_dir.lower().replace("_", " ")
    
    crime = c.execute('SELECT type_of_crime FROM criminals WHERE name=? COLLATE NOCASE', (person_name,)).fetchone()
    print(crime)
    # Create an empty list to store face encodings for the person
    face_encodings_list = []

    # Loop through all image files in the person's folder
    for filename in os.listdir(os.path.join(parent_dir, person_dir)):
        # Load the image file
        image = face_recognition.load_image_file(os.path.join(parent_dir, person_dir, filename))

        # Detect face locations in the image
        face_locations = face_recognition.face_locations(image)
        if len(face_locations)!=0:
            # Generate face encodings for the image
            face_encodings = face_recognition.face_encodings(image, face_locations)[0]

        # Add the face encodings to the list for the person
        face_encodings_list.append(face_encodings)
    if crime != None:
        crime_data[person_name] = crime
    
    else:
        crime_data[person_name] = "No record"
    
    # Add the face encodings list to the dictionary for the person
    face_encodings_dict[person_name] = face_encodings_list


# Save the face encodings dictionary to a file using pickle
with open("face_encodings.pkl", "wb") as f:
    pickle.dump(face_encodings_dict, f)

# Load the saved face encodings from the file
with open("face_encodings.pkl", "rb") as f:
    saved_encodings = pickle.load(f)

# model_new = torch.hub.load('ultralytics/yolov5', 'custom', path='crowdhuman_yolov5m.pt')
prevCam = None
record = pd.DataFrame(columns = ["Name", "Movement"])

def detectface(frame, bboxes, img3, streamTable, cameraNo, idValue):
# def detectface(frame, bboxes, cameraNo, idValue):
    global prevCam, record
    # print(bboxes)
    for bbox in bboxes:
        bbox = bbox.tolist()[0]
        # print(bbox)
        x1 = int(bbox[0])
        y1 = int(bbox[1])
        x2 = int(bbox[2])
        y2 = int(bbox[3])
        crop = frame[y1:y2, x1:x2]

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(crop)
        face_encodings = face_recognition.face_encodings(crop, face_locations)
        tracking_ids = []
        # Loop through each face in this frame of video
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare the face encodings of the current frame with the saved encodings
            for name, encodings in saved_encodings.items():
                crime = crime_data[name]
                for encoding in encodings:
                    distance = face_recognition.face_distance([encoding], face_encoding)
                    threshold = 0.6 # Adjust this value based on the accuracy you want
                    if distance < threshold:
                        # Create a table
                        if cameraNo != prevCam:
                            # movement = f"{prevCam} ---> {cameraNo}"
                            movement = f"Standing in room {cameraNo}"
                        else:
                            prevCam = cameraNo
                            movement = "Standing in {cameraNo}"
                        
                        if name in record["Name"].values:
                            record.loc[(record["Name"]==name)] = name, movement
                        else:
                            new_row = {"Name": name, "Movement": movement}
                            record = record.append(new_row, ignore_index=True)
                        streamTable.table(record)
                        cv2.rectangle(crop, (left, top), (right, bottom), (0, 255, 0), 2)
                        cv2.putText(crop, name+" "+str(crime), (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        # Display the resulting image
                        cv2.imshow('Video', crop)
                        img3.image(crop)
                        with open("tracking_ids.txt","r") as f:
                            if name not in f.read():
                                with open("tracking_ids.txt","a") as f:
                                    f.writelines(str(idValue)+" "+str(name))
                                    f.write("\n")
                        
        # return tracking_ids


# import streamlit as st
# import sqlite3
# import pandas as pd
# from streamlit_ace import st_ace, KEYBINDINGS, LANGUAGES, THEMES
# import streamlit_toggle as tog
# from pathlib import Path
# import os

# def create_connection(db_file):
#     """ create a database connection to the SQLite database
#     specified by the db_file
# :param db_file: database file
# :return: Connection object or None
# """
#     conn = None
#     try:
#         conn = sqlite3.connect(db_file)
#     except Exception as e:
#         st.write(e)

#     return conn


# def create_database():
#         st.markdown("# Create Database")

#         st.info("""A database in SQLite is just a file on same server. 
#         By convention their names always must end in .db""")


#         db_filename = st.text_input("Database Name")
#         create_db = st.button('Create Database')
        
#         conn = create_connection('default.db')
#         mycur = conn.cursor() 
#         mycur.execute("PRAGMA database_list;")
#         available_table=(mycur.fetchall())
#         with st.expander("Available Databases"): st.write(pd.DataFrame(available_table))
        
#         if create_db:
            
            
#             if db_filename.endswith('.db'):
#                 conn = create_connection(db_filename)

#                 st.success("New Database has been Created! Please move on to next tab for loading data into Table.")
#             else: 
#                 st.error('Database name must end with .db as we are using sqlite in the background to create files.')

# def upload_data():
#         st.markdown("# Upload Data")
#         sqlite_dbs = [file for file in os.listdir('.') if file.endswith('.db')]
#         db_filename = st.selectbox('Database', sqlite_dbs)
#         table_name = st.text_input('Table Name to Insert')
#         conn = create_connection(db_filename)
#         uploaded_file = st.file_uploader('Choose a file')
#         upload = st.button("Create Table")
#         if upload:
#             #read csv
#             try:
#                 df = pd.read_csv(uploaded_file)
#                 df.to_sql(name=table_name, con=conn)
#                 st.write('Data uploaded successfully. These are the first 5 rows.')
#                 st.dataframe(df.head(5))

#             except Exception as e:
#                 st.write(e)

# intro, db, tbl, qry = st.tabs(["1 Intro to SQL","2 Create Database", "3 Upload Data", "4 Query Data"])

# with intro:
#     # st.write((Path(__file__).parent/"data/sql.md").read_text()) 
#     with db:
#         create_database()
#     with tbl: 
#         upload_data()
#     with qry:
#         sqlite_dbs = [file for file in os.listdir('.') if file.endswith('.db')]
#         db_filename = st.selectbox('DB Filename', sqlite_dbs)
#         conn = create_connection(db_filename)
#         mycur = conn.cursor() 
#         mycur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
#         available_table=(mycur.fetchall())
#         st.write("Available Tables")
#         st.dataframe(pd.DataFrame(available_table))
#         with readme("streamlit-ace"):
#             c1, c2 = st.columns([3, 0.5])

#             # c2.subheader("Parameters")
#             # st.write(LANGUAGES)
#             with c2: 
#                 st.write("")
#                 st.write("")
#                 st.write("")
#                 st.write("")
#                 dark_mode = tog.st_toggle_switch(label="Dark", 
#                             key="darkmode", 
#                             default_value=False, 
#                             label_after = False, 
#                             inactive_color = '#D3D3D3', 
#                             active_color="#11567f", 
#                             track_color="#29B5E8"
#                             )
#                 if dark_mode: THEME = THEMES[0]
#                 else: THEME = THEMES[3]
#             with c1:
#                 st.subheader("Query Editor")
#                 content = st_ace(
#                     placeholder="--Select Database and Write your SQL Query Here!",
#                     language= LANGUAGES[145],
#                     theme=THEME,
#                     keybinding=KEYBINDINGS[3],
#                     font_size=c2.slider("Font Size", 10, 24, 16),
#                     min_lines=15,
#                     key="run_query",
#                 )

#                 if content:
#                     st.subheader("Content")
                    
#                     st.text(content)
                    
#                     def run_query():
#                         query = content
#                         conn = create_connection(db_filename)

#                         try:
#                             query = conn.execute(query)
#                             cols = [column[0] for column in query.description]
#                             results_df= pd.DataFrame.from_records(
#                                 data = query.fetchall(), 
#                                 columns = cols
#                             )
#                             st.dataframe(results_df)
#                             export = results_df.to_csv()
#                             st.download_button(label="Download Results", data=export, file_name='query_results.csv' )
#                         except Exception as e:
#                             st.write(e)

#                     run_query()