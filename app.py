import streamlit as st
import requests
import pandas as pd
from shapely.geometry import mapping, Polygon
import json
import tempfile
import zipfile
import os
from io import BytesIO
import time

# Disable the submit button after it is clicked 
def disable_login():
    st.session_state.login_disabled = True

def disable_download():
    st.session_state.download_disabled = True
    
# Initialize disabled states for form_submit_button to False
if "login_disabled" not in st.session_state:
    st.session_state.login_disabled = False

if "download_disabled" not in st.session_state:
    st.session_state.download_disabled = False

def return_menu():
    # Clear session state related to login
    st.session_state.pop("selected_theme", None)
    st.session_state.pop("login_disabled", None)
    st.session_state.pop("download_disabled", None)
    # Enable form submission button
    st.session_state.login_disabled = False
    st.session_state.download_disabled = False
    # Reset stage to 0
    st.session_state.stage = 0
    
def thank_you():
    thanks = st.toast('Success, thank you!', icon="✅")
    time.sleep(4) # Wait for 4 seconds
    thanks.empty() # Clear the alert
    # Clear session state related to login
    st.session_state.pop("selected_theme", None)
    st.session_state.pop("login_disabled", None)
    st.session_state.pop("download_disabled", None)
    # Enable form submission button
    st.session_state.login_disabled = False
    st.session_state.download_disabled = False
    # Reset stage to 0
    st.session_state.stage = 0

# Function to fetch themes from API
def fetch_themes(username, password):
    # Get access token
    auth_url = "https://www.onemap.gov.sg/api/auth/post/getToken"
    auth_payload = {
        "email": username,
        "password": password
    }
    auth_response = requests.post(auth_url, json=auth_payload)
    if auth_response.status_code == 200:
        token = auth_response.json().get("access_token")
        headers = {"Authorization": token}
        # Fetch themes
        url = "https://www.onemap.gov.sg/api/public/themesvc/getAllThemesInfo?moreInfo=Y"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            themes_data = response.json().get("Theme_Names", [])
            return themes_data, token  # Return the token along with themes_data
        else:
            st.error("Failed to fetch themes. Please check your credentials.")
    else:
        st.error("Failed to authenticate. Please check your credentials.")
        return None, None  # Return None for themes_data and token


# Function to download selected themes
def download_themes(themes_data, selected_theme, token):
    headers = {"Authorization": token}
    
    querynames_list = [] 

    for i in range(len(themes_data)):
        for k in selected_theme:
            if themes_data[i]["THEMENAME"] == k:
                querynames_list.append(themes_data[i]["QUERYNAME"])

    download_files = []

    for i in querynames_list: 
        url = "https://www.onemap.gov.sg/api/public/themesvc/retrieveTheme?queryName=" + i
        response = requests.request("GET", url, headers=headers)
        json_data = response.json()
        
        # Removes meta from the 'SrchResults' array
        json_data['SrchResults'] = json_data['SrchResults'][1:]
        
        # Extract the list of dictionaries from 'SrchResults'
        data_list = json_data['SrchResults']
        
        # Create a temporary file to save the download
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv' if 'Point' in [item.get('Type') for item in data_list] else '.geojson')
        download_path = temp_file.name
            
        # Iterate over each item in the list
        for item in data_list:
            type_value = item.get('Type')

            if type_value == "Point":  
                # Convert list of dictionaries to DataFrame
                df = pd.DataFrame(data_list)

                # Split LatLng column into separate latitude and longitude columns
                df[['LATITUDE', 'LONGITUDE']] = df['LatLng'].str.split(',', expand=True)

                # Drop the original latlong column
                df.drop(columns=['LatLng'], inplace=True)

                # Save DataFrame as csv
                df.to_csv(download_path, index = False)

                # Update status 
                print(f"CSV file: {i}.csv has been downloaded")
            
            elif type_value == "Polygon" or type_value == "Line":
                # Extract coordinates and create GeoJSON feature collection
                features = []
                for item in data_list:
                    coordinates = item['LatLng']
                    if type_value == "Line":
                        # If it's a line, treat it as a polygon with single ring
                        coordinates.append(coordinates[0])  # Close the line

                    geometry = Polygon(item['LatLng'])
                    feature = {
                        'type': 'Feature',
                        'geometry': mapping(geometry),
                        'properties': {key: value for key, value in item.items() if key != 'LatLng'}
                    }
                    features.append(feature)

                feature_collection = {'type': 'FeatureCollection', 'features': features}

                # Save to GeoJSON file
                with open(download_path, 'w') as f:
                    json.dump(feature_collection, f)

                # Update status 
                print("geojson file: " + i + " has been downloaded")

            else: 
                print("Error: data is neither point, line or polygon.")

        download_files.append((i, download_path))

    return download_files

# Main function
def main():
    st.set_page_config(
        page_title="OneMap API Thematic Layer Downloader",
        page_icon="⬇️")
    
    if 'stage' not in st.session_state:
        st.session_state.stage = 0
    
    st.title("OneMap API Thematic Layer Downloader")
    st.write("This app allows users to download thematic layers from the OneMap API. You must have an existing OneMap API account to use this service. Otherwise, you may register for one [here](https://www.onemap.gov.sg/apidocs/register).")
    
    # First form for username and password
    with st.form("login_form"):
        st.write("Enter Your Credentials:")
        username = st.text_input("Username", value=st.session_state.get("username", ""))
        password = st.text_input("Password", type="password", value=st.session_state.get("password", ""))
        submitted = st.form_submit_button("Login and Fetch Themes", on_click=disable_login, disabled=st.session_state.login_disabled)

    selected_theme = None  # Initialize selected_theme to avoid UnboundLocalError

    if submitted:
        st.session_state["username"] = username
        st.session_state["password"] = password
        st.session_state.stage = 1
        
    submit_theme_selection = None  # Initialize outside of the conditional block
    if st.session_state.stage == 1:
        if not (username and password):
            st.info("Reset to enter username and password")
        
        if username and password:
            themes_data, token = fetch_themes(username, password)  # Get the token from fetch_themes
            if themes_data and token:
                st.info("Login successful!")
                themes = [theme["THEMENAME"] for theme in themes_data]
                with st.form(key='theme_selection_form'):
                    selected_theme = st.multiselect("Select Theme(s):", themes, default=st.session_state.get("selected_theme", []))
                    submit_theme_selection = st.form_submit_button(label='Get Themes Data', on_click=disable_download, disabled=st.session_state.download_disabled)

    if submit_theme_selection:
        if selected_theme:
            st.session_state.stage = 2
            st.session_state["selected_theme"] = selected_theme  # Store selected themes in session state

    if st.session_state.stage == 2:
        if selected_theme:  # Check if selected_theme is valid
            headers = {"Authorization": token}  # Get headers from token
            # Perform download of selected themes
            st.success("Preparing themes...")
            download_files = download_themes(themes_data, selected_theme, token)  # Pass the headers to download_themes
            
            # Create a ZIP file in memory
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                for theme_name, download_path in download_files:
                    zipf.write(download_path, f"{theme_name}.csv" if download_path.endswith(".csv") else f"{theme_name}.geojson")
            zip_buffer.seek(0)

            st.success("Data ready :-)")
            # Provide a download button for the ZIP file
            
            submit_download = st.download_button(
                label="Download All Selected Themes as ZIP",
                data=zip_buffer,
                file_name='selected_themes.zip',
                mime='application/zip',
                on_click = thank_you)

    st.button('Reset', on_click=return_menu)

    # Footer
    footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #F0F0F5;
        text-align: center;
        padding: 10px;
        color: #333333;
    }
    </style>
    <div class="footer">
    <p>made with ♡ by @meganannpang</p>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)

# Run the main function
if __name__ == "__main__":
    main()
