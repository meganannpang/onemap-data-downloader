# OneMap API Theme Downloader

## Overview

The OneMap API Theme Downloader built on Streamlit is an application designed to streamline the process of accessing and downloading thematic data from the OneMap API. This tool allows users to authenticate using their OneMap API token, select multiple themes, and download the data in a convenient zip file. The application supports point data saved as CSV files and line and polygon data saved as GeoJSON files.

## Features

- **User Authentication:** Secure login using OneMap API token based on the provided username and password.
- **Theme Selection:** View themes available in a dropdown menu and select multiple themes available via the OneMap API.
- **Dynamic Dropdown Menu:** User selected themes are removed from the dropdown menu upon selection and displayed in a selection bar for easy reference.
- **Theme Management:** Ability to remove themes from the selection bar if selected erroneously.
- **Data Retrieval and Parsing:** Automatically query the `queryname` for each selected theme, fetch the data, and parse it accordingly.
- **File Preparation:** Data is saved in appropriate formats (CSV for point data, GeoJSON for line and polygon data) and packaged in a zip file.
- **Easy Download:** Download the zip file with all selected themes to the default Downloads folder.

## How It Works

### 1. Authentication

The application authenticates and accesses the user’s OneMap API token based on the username and password provided.

### 2. Fetching Available Themes

Upon successful authentication, the app fetches the list of themes available via the OneMap API at the time of using the app.

#### 2.1 Viewing Themes

- Users can view the list of themes in a dropdown menu.
- Multiple selections are allowed.

#### 2.2 Managing Selected Themes

- Selected themes are removed from the dropdown menu and placed in the selection bar for easy reference.
- Users can remove selected themes from the selection bar if selected erroneously.

### 3. Querying Theme Data

Once the selection is confirmed, the app proceeds to query for the `queryname` accompanying each selected theme.

#### 3.1 Understanding `queryname`

- `queryname` is a unique identifier tied to each theme available on the OneMap API.

#### 3.2 Fetching Data

- Using the `queryname`, the app fetches the data from the OneMap API and parses the API response/data accordingly.
- By default, point data is saved as CSV, while line and polygon data are saved in GeoJSON format.

### 4. Preparing Files

The files are prepared in a zip file which users can download in a single click.

### 5. Downloading Files

The zip file containing all the selected themes will be downloaded to the Downloads folder by default.

#### 5.1 Naming Convention

- Files are named using the convention `{queryname}.csv` for point data and `{queryname}.geojson` for line and polygon data.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

## Disclaimer

This app was developed as a personal passion project. Feel free to use it at your own risk. 

---

This README provides an overview of the OneMap API Theme Downloader application, detailing its functionality and usage. It is also AI generated. For more details about the project, you may visit my Notion page: bit.ly/proj-omdl
