# Traffic Management Portal 🚦

A comprehensive Flask web application for analyzing traffic congestion economic costs, including fuel consumption, CO₂ emissions, and productivity loss calculations.

![Traffic Analysis](https://img.shields.io/badge/Python-Flask-green) ![License](https://img.shields.io/badge/License-MIT-blue) ![Status](https://img.shields.io/badge/Status-Live-success)

## 🌟 Features

- **Data Entry Form**: Easy input of traffic data including location, vehicle types, volumes, and travel times
- **Economic Analysis**: Calculates:
  - Excess fuel consumption and costs
  - CO₂ emissions from congestion
  - Productivity loss in monetary terms
- **Visual Reports**: Interactive charts and graphs
- **PDF Export**: Professional report generation
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Live Demo

The application is currently running at: `http://127.0.0.1:5000/`

## 🛠️ Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Chart.js
- **PDF Generation**: ReportLab
- **Database**: JSON file storage

## 📊 Methodology

The application uses proven traffic engineering formulas:

1. **Delay Time Calculation**: Actual Travel Time - Free-Flow Travel Time
2. **Excess Fuel Consumption**: (Fuel Rate in Congestion - Fuel Rate at Free Flow) × Distance
3. **CO₂ Emissions**: Excess Fuel × Emission Factor (2.31 kg CO₂/liter for petrol)
4. **Productivity Loss**: Delay Time × Average Occupancy × Value of Time

## 📦 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Stevenson80/Traffic_Management_Project.git
cd Traffic_Management_Project

# Install dependencies
pip install -r requirements.txt

#Run the application
python app.py

#Open your browser
Navigate to: http://127.0.0.1:5000/

Traffic_Management_Project/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── script.js     # JavaScript functionality
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── data_entry.html   # Data input form
│   ├── analyze.html      # Analysis interface
│   ├── results.html      # Results display
│   └── data_success.html # Success confirmation
└── utils/                # Utility functions
    ├── calculations.py   # Business logic calculations
    └── report_generator.py # PDF report generation

Usage
Enter Data: Use the Data Entry page to input traffic information

Analyze: Select a location and date range to analyze

View Results: See detailed economic cost breakdowns with charts

Export: Download PDF reports for documentation and presentations

👨‍💻 Developer
Oladotun Ajakaiye
Service Manager and Data Analyst
Opygoal Technology Ltd

📧 Email: soajakaiye@gmail.com

🔗 LinkedIn: https://www.linkedin.com/in/steven-ajakaiye-1b243b27/

🌐 Website: https://opygoaltechnology.onrender.com/

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Traffic engineering methodologies based on international standards

Bootstrap for responsive UI components

Flask community for excellent documentation

© 2025 Opygoal Technology Ltd. All rights reserved.
