# FastFileStore Backend Server<img src="app_icon.png" alt="App Icon" width="100" align="right">

This repository contains the backend server for FastFileStore, a cloud file storage app written in python. This Django program handles the server-side operations such as database management and file storage for the GUI app. You can find the app [here](https://github.com/therockey/FFS-GUI).

## Prerequesites

**In order for the server to function properly, you need to have 7-Zip installed in your system, and added to your PATH env variable.**

You can find 7-Zip [here](https://www.7-zip.org/)

## Installation

To run the FastFileStore server locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/JanSzyndlarewicz/FFS-API.git
   cd FFS-API
   ```
2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Add your server IP address/addresses to the allowed hosts list in Server/settings.py:**  
   *example:*
   ```python
   ALLOWED_HOSTS = ['192.168.0.100']
   ```
6. **Create the database migrations**
   ```bash
   python ./manage.py makemigrations Server
   ```
5. **Apply the migrations:**
   ```bash
   python ./manage.py migrate
   ```
5. **Start the app with the correct IP and port:**  
   *example:*
   ```bash
   python ./manage.py runserver 192.168.0.100:8000
   ```
   
## About
FastFileStore is designed to provide a fast and efficient way to store and manage files. The application is divided into two main parts: the backend server and the GUI app.

I took the lead on developing the backend server. The server is built with Python and uses Django for the web framework and [SQLite](https://sqlite.org/) for the database. It provides a robust API for managing files, including operations like uploading, downloading, and deleting files. The server also includes features like file encryption and access control for added security. Logging is also available and enabled by default; information about server events will be outputted to Server/application.log file.

## Contact
If you have any questions or feedback, feel free to reach out:

**Jan Szyndlarewicz**
   - GitHub: [JanSzyndlarewicz](https://github.com/JanSzyndlarewicz)

**Kacper Tomczyk**
   - Email: kacperus.tomczyk@gmail.com
   - GitHub: [therockey](https://github.com/therockey)

<br><br>
*This project is maintained by [JanSzyndlarewicz](https://github.com/JanSzyndlarewicz)*
