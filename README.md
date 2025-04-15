# Deepfake Audio Detection

## Project Description

This project is a web application designed to detect deepfake audio using machine learning models. The application allows users to upload audio files, analyze them for deepfake characteristics, and generate detailed reports. The project leverages various libraries and tools such as Flask for the web framework, TensorFlow and Keras for the machine learning models, and `wkhtmltopdf` for generating PDF reports.

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.7 or higher
- `wkhtmltopdf` for PDF generation

## Dependencies

Install the required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

## Setup

1. **Install `wkhtmltopdf`:**
   - Download and install `wkhtmltopdf` from the [official website](https://wkhtmltopdf.org/downloads.html).
   - Ensure the executable path is correctly set in the `app.py` file:
     ```python
     path_to_wkhtmltopdf = r'B:\wkhtmltopdf\bin\wkhtmltopdf.exe'
     config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)
     ```

2. **Database Setup:**
   - Ensure the SQLite database is set up and the `get_db_connection` function in `database.py` is correctly configured to connect to your database.

3. **Static and Template Files:**
   - Ensure the `static` and `templates` directories are correctly set up with the necessary files.

## Running the Application

To run the application, execute the following command:

```bash
python app.py
```

The application will start in debug mode and can be accessed at `http://127.0.0.1:8000`.

## Usage

1. **Upload Audio File:**
   - Navigate to the upload page and upload a `.wav` audio file.

2. **Analyze Audio:**
   - The application will analyze the uploaded audio file and display the results.

3. **Download Report:**
   - You can download a detailed report of the analysis in PDF format.

## Project Structure

- `app.py`: Main application file.
- `database.py`: Database connection setup.
- `static/`: Directory for static files (e.g., CSS, JavaScript, images).
- `templates/`: Directory for HTML templates.
- `requirements.txt`: List of dependencies.

## License

This project is licensed under the MIT License.
