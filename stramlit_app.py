from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st
import io
from io import StringIO
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import json
import time

def authenticate():
    global SERVICE_ACCOUNT_FILE
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_FILE,
                                                                    scopes=SCOPES)
    return creds


def download_file(filename):

    creds = authenticate()

    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)

        query = "name contains " + "'"+ filename +"' and trashed = false"
        response = service.files().list(q=query, fields= 'files(id,name)').execute()
        files = response.get('files')
        
        if len(files)>0:
            file_id = files[0]['id']

            request = service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}.")
        else:
            file=None

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file.getvalue()


SERVICE_ACCOUNT_FILE = st.file_uploader('Upload "service account file" in ".json" format.', type='json')


if SERVICE_ACCOUNT_FILE is not None:

    SERVICE_ACCOUNT_FILE = json.load(SERVICE_ACCOUNT_FILE)

    col_names = st.text_input('enter column names to be plotted with comma seperator:')
    date_col_name = st.text_input('enter date column name to be plotted on x axes:')

    filename = st.text_input('enter the filename of the file in Drive:')

    if filename:

        while True:

            file = download_file(filename)

            if file is not None:
                file = file.decode('utf-8')
                df = pd.read_csv(StringIO(file), index_col=0)

                col_data = {}

                for col_name in col_names.split(','):
                    col_data[col_name] = df[col_name].to_numpy()

                date_data = df[date_col_name].to_numpy()

                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=("Plot 1", "Plot 2", "Plot 3", "Plot 4"))


                fig.add_trace(go.Scatter(x=date_data, y=list(col_data.values())[0]),
                            row=1, col=1)

                fig.add_trace(go.Scatter(x=date_data, y=list(col_data.values())[1]),
                            row=1, col=2)

                fig.add_trace(go.Scatter(x=date_data, y=list(col_data.values())[2]),
                            row=2, col=1)

                fig.add_trace(go.Scatter(x=date_data, y=list(col_data.values())[3]),
                            row=2, col=2)

                fig.update_layout(height=500, width=1300,
                                title_text="Multiple Subplots with Titles")

                st.write(fig)

            time.sleep(47)