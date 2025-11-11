# Debugging and Monitoring Tool

A tool that automatically reads logs, finds errors, and suggests possible solutions using AI. This project includes a real-time monitoring dashboard to make debugging faster and easier.

## Project Structure

```
debugging_and_monitoring_tool/
├── frontend/                  # Frontend code (HTML, CSS, JavaScript)
│   ├── css/                   # CSS styles
│   ├── js/                    # JavaScript files
│   └── index.html             # Main HTML file
└── backend/                   # Flask backend
    ├── logs/                  # Log storage
    ├── app.py                 # Main Flask application
    └── requirements.txt       # Python dependencies
```

## Features

- **Log Management**: Collects logs and stores them safely in a file
- **AI Debugging**: Uses machine learning to read logs, classify errors, and suggest fixes
- **Dashboard & Alerts**: React.js web dashboard to show logs, errors, and send alerts for critical issues

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python Flask
- **Database**: JSON file storage (can be extended to MongoDB or PostgreSQL)
- **AI**: Python ML/NLP libraries

## How to Run

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the Flask application:
   ```
   python app.py
   ```

### Frontend Setup

1. Open the `index.html` file in a web browser

## Usage

1. The dashboard will display log statistics and a table of log entries
2. Use the filters to view logs by severity or service
3. Click on a log entry to view details
4. Use the AI analysis button to get suggestions for fixing errors

## Project Status

This project is currently at 70% completion with the following components implemented:
- Basic project structure
- Backend Flask API with log management
- Frontend dashboard with visualization
- Sample data for testing

## Next Steps

- Complete the AI debugging module with more advanced ML models
- Implement real-time alerts and notifications
- Add user authentication
- Extend database support for MongoDB or PostgreSQL