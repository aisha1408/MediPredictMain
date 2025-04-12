# MediPredictMain
To predict future number of available resources based on historic data.

## Overview
MediPredict is an AI-powered dashboard that helps hospitals predict patient admissions, estimate the average length of stay (LOS), and forecast bed and staff needs. Using historical hospital data, the system applies machine learning models (Prophet and Random Forest) to predict future resource demands and help administrators make better decisions in advance.

## Features
- **Patient Admissions Forecasting**: Predict the number of patient admissions over the next 30 days.
- **Length of Stay (LOS) Prediction**: Estimate the average length of stay based on historical data.
- **Bed & Staff Needs Forecasting**: Calculate required beds and staff for the next 30 days based on predicted admissions.
- **ICU Equipment Forecasting**: Predict the usage of ICU equipment for the next 30 days.
- **Emergency Case Forecasting**: Forecast the number of emergency cases for the next 30 days.
- **Department-wise Patient Forecasting**: Forecast the number of patients in different departments for the next 30 days.

## Requirements
- Python 3.x
- Required Python libraries:
  - `pandas`
  - `numpy`
  - `prophet`
  - `sklearn`
  - `streamlit`
  - `matplotlib`
  - `json`
  - `hashlib`
  - `os`

## Installation
1. Clone the repository or download the code files.
2. Install the required dependencies by running:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app using Streamlit:
   ```bash
   streamlit run app.py
   ```

## Usage
### Authentication
- Users must log in or register to access the dashboard.
- The login and registration are handled using a local JSON file (`users.json`) where user credentials are stored securely.

### Data Upload
- Users need to upload several CSV files containing historical hospital data:
  - Admissions data (date, admissions)
  - Patient demographics (patient_id, age, gender, etc.)
  - Discharge logs (patient_id, admission_date, discharge_date)
  - ICU equipment usage (date, ventilators_used, beds_occupied, etc.)
  - Staff rosters (date, staff_count)
  - Emergency cases (date, emergency_cases)
  - Department-wise patient data (date, department, patient_count)
- The dashboard uses these datasets to predict future resource needs.

### Dashboard Features
1. **Patient Admissions Forecast**: A line chart showing the predicted patient admissions for the next 30 days.
2. **Length of Stay (LOS) Prediction**: A metric displaying the predicted average length of stay.
3. **Bed & Staff Needs**: A table and line chart displaying the predicted bed and staff requirements for the next 30 days.
4. **ICU Equipment Usage**: Line charts for the forecasted ICU equipment usage over the next 30 days.
5. **Emergency Case Forecast**: A line chart showing the predicted number of emergency cases.
6. **Department-wise Patient Forecast**: Line charts for each department showing the predicted patient count.

## File Format
Each CSV file must contain the following columns:
1. **Admissions CSV**: `date`, `admissions`
2. **Demographics CSV**: `patient_id`, `age`, `gender`, ...
3. **Discharge CSV**: `patient_id`, `admission_date`, `discharge_date`
4. **ICU CSV**: `date`, `ventilators_used`, `beds_occupied`, ...
5. **Staff CSV**: `date`, `staff_count`
6. **Emergency CSV**: `date`, `emergency_cases`
7. **Department-wise CSV**: `date`, `department`, `patient_count`

## How It Works
1. **Modeling**:
   - **Prophet** is used to forecast patient admissions, ICU equipment usage, and emergency cases.
   - **Random Forest Regressor** is used to predict the average length of stay (LOS).
2. **Data Visualization**:
   - The dashboard uses `Streamlit` to provide an interactive UI where users can upload data and view predictions.
   - `Matplotlib` is used for generating charts that visualize predictions over the next 30 days.
![image](https://github.com/user-attachments/assets/3296be67-3302-4cbf-aea8-2fe942551dab)
![image](https://github.com/user-attachments/assets/9fd49299-3cde-431d-9711-ea563586674f)
![image](https://github.com/user-attachments/assets/ba1fc690-ae7a-45f4-b4b0-2f4d1832ec5e)


## Contributing
1. Fork the repository.
2. Create a new branch for your changes.
3. Commit your changes and push them to your branch.
4. Open a pull request with a detailed description of your changes.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
For questions or support, please contact gamulya55@gmail.com, harinis2407@gmail.com, aishanizarhussain7@gmail.com


