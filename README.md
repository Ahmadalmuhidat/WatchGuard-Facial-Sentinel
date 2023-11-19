# WatchGuard Facial Sentinel

## Overview
The WatchGuard Facial Sentinel is a comprehensive system designed to assist in identifying wanted individuals by utilizing advanced facial recognition technology. This program allows users to upload information and images of wanted individuals, storing this data securely in a database. The system then connects to all available cameras linked to the PC, analyzing their streams in real-time. If a target person appears in any camera feed, the WatchGuard Facial Sentinel triggers an alert, notifying the user of the presence of the wanted individual.

## Features
- **Upload Wanted Individuals:** Users can upload information about wanted people along with their images to the program.
- **Database Storage:** All uploaded data is securely stored in a database for future reference.
- **Real-time Camera Stream Analysis:** The WatchGuard Facial Sentinel connects to available cameras and continuously analyzes their feeds for faces.
- **Facial Recognition:** Utilizes sophisticated facial recognition algorithms to match faces in camera feeds with the uploaded images of wanted individuals.
- **Alert System:** Upon detecting a match, the program generates an alert to notify the user of the presence of the wanted person.

## Installation
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Ahmadalmuhidat/WatchGuard-Facial-Sentinel.git
   cd watchguard-facial-sentinel
2. **Install Dependencies**: Ensure all required dependencies are installed. Use the following command to install Python dependencies:

    ```bash
    pip install -r requirements.txt
3. **Database Setup**: Configure the database settings by providing the necessary credentials in the designated configuration file.
Camera Connection: Ensure all cameras intended for monitoring are connected and accessible by the PC.

## Usage
1. **Start the Program**:

    ```bash
    python watchguard.py
1. **Upload Wanted Individuals**:
        Access the program's interface to upload information and images of wanted individuals.
        Ensure the data is correctly entered and stored in the database.

1. **Monitoring**:
        The WatchGuard Facial Sentinel will automatically start analyzing camera feeds upon execution.
        Alerts will be generated if a wanted person is detected.

## Configuration
Database Configuration: Edit the database configuration file to specify the database type, credentials, and connection details.
Camera Settings: Configure camera settings if necessary, such as resolution, frame rate, or specific camera selection.

## Contributing
Contributions to this project are welcome. If you'd like to contribute:
* Fork the repository.
* Create your branch: git checkout -b feature/your-feature
* Commit your changes: git commit -am 'Add your feature'
* Push to the branch: git push origin feature/your-feature
* Submit a pull request.

## Acknowledgments
This project utilizes the [face_recognition](https://github.com/ageitgey/face_recognition) library for facial recognition capabilities. Special thanks to the contributors and maintainers of this library for their invaluable work.

## Support
For any issues or inquiries, please contact ahmad.almuhidat@gmail.com.
