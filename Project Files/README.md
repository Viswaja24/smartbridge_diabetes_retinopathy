# Diabetic Retinopathy Detection App

## Overview
This is a web application that uses Deep Learning (Transfer Learning with InceptionV3/Xception) to detect Diabetic Retinopathy from retinal fundus images. It classifies the condition into 5 stages: No DR, Mild, Moderate, Severe, and Proliferative DR.

## Prerequisites

Before running the application, ensure you have the following installed:
*   [Python 3.8+](https://www.python.org/downloads/)
*   [pip](https://pip.pypa.io/en/stable/installation/)

## Setup & Installation

1.  **Clone or Download the Repository**
    Navigate to the project directory:
    ```bash
    cd smartbride_diabetes_retinopathy
    ```

2.  **Create a Virtual Environment (Recommended)**
    It's best practice to run Python apps in a virtual environment to avoid dependency conflicts.
    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate

    # Mac/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    Install the required Python packages using `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Model Setup**
    *   **Crucial Step**: You need the trained model file for predictions to work.
    *   Find or download your trained model file named `Updated-Xception-diabetic-retinopathy.h5`.
    *   Place this file inside the `model/` directory.
    *   **Note**: If the model is missing, the app will launch, but prediction features will fail.

5.  **Database Setup **
    *   The app is configured to use IBM Cloudant.
    *   To enable it, open `app.py` and replace the placeholder credentials:
        ```python
        client = Cloudant.iam('your_username', 'your_apikey', connect=True)
        ```

## Running the Application

1.  **Start the Flask Server**
    ```bash
    python app.py
    ```

2.  **Access the App**
    Open your web browser and go to:
    [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Usage
1.  Go to the **Prediction** page.
2.  Upload a retinal fundus image (supported formats: JPG, PNG).
3.  Click **Analyze Image**.
4.  View the prediction result and the severity stage.
