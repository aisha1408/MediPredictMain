from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  
import hashlib
import os
import json
import io
import base64
from datetime import datetime, timedelta
import tempfile

app = Flask(__name__)
app.secret_key = "medipredict_secret_key"  

USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            json.dump({}, f)
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    users = load_users()
    if username in users:
        return False, "Username already exists!"
    users[username] = hash_password(password)
    save_users(users)
    return True, "Account created successfully."

def authenticate_user(username, password):
    users = load_users()
    return username in users and users[username] == hash_password(password)


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if authenticate_user(username, password):
        session['username'] = username
        return redirect(url_for('dashboard'))
    return render_template('index.html', login_error="Invalid username or password")

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    
    success, msg = register_user(username, password)
    if success:
        return render_template('index.html', register_success=msg)
    else:
        return render_template('index.html', register_error=msg)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', username=session['username'])


def create_figure_to_base64(plt):
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    string = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return string


def forecast_time_series(df, date_col, value_col, periods=30):
    df = df.sort_values(by=date_col)
    
 
    df['day_of_week'] = df[date_col].dt.dayofweek
    df['day_of_month'] = df[date_col].dt.day
    df['month'] = df[date_col].dt.month
    df['year'] = df[date_col].dt.year
    
   
    df['time_idx'] = np.arange(len(df))
    

    features = ['time_idx', 'day_of_week', 'day_of_month', 'month']
    X = df[features]
    y = df[value_col]
    

    model = LinearRegression()
    model.fit(X, y)
    

    last_date = df[date_col].max()
    future_dates = [last_date + timedelta(days=i+1) for i in range(periods)]
    
 
    future_df = pd.DataFrame({
        date_col: future_dates,
        'day_of_week': [d.dayofweek for d in future_dates],
        'day_of_month': [d.day for d in future_dates],
        'month': [d.month for d in future_dates],
        'time_idx': np.arange(len(df), len(df) + periods)
    })
    
    future_X = future_df[features]
    predictions = model.predict(future_X)
  
    all_dates = list(df[date_col]) + future_dates
    all_values = list(df[value_col]) + list(predictions)
 
    plt.figure(figsize=(10, 6))
    plt.plot(df[date_col], df[value_col], label='Historical')
    plt.plot(future_dates, predictions, label='Forecast', linestyle='--')
    plt.xlabel('Date')
    plt.ylabel(value_col)
    plt.title(f'{value_col} Forecast')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plot_img = create_figure_to_base64(plt)
    
    return {
        'dates': [d.strftime('%Y-%m-%d') for d in future_dates],
        'values': predictions.tolist(),
        'chart': plot_img
    }

@app.route('/api/process-data', methods=['POST'])
def process_data():
    try:
 
        required_files = ['admissions', 'demographics', 'discharge', 'icu', 'staff']
        for file_key in required_files:
            if file_key not in request.files or request.files[file_key].filename == '':
                return jsonify({'error': f'Missing required file: {file_key}'})
        
     
        temp_dir = tempfile.mkdtemp()
        file_paths = {}
        
        for file_key in request.files:
            if request.files[file_key].filename != '':
                file_path = os.path.join(temp_dir, request.files[file_key].filename)
                request.files[file_key].save(file_path)
                file_paths[file_key] = file_path
        
        
        results = {}
        
       
        try:
            ad_df = pd.read_csv(file_paths['admissions'])
            ad_df.columns = ad_df.columns.str.lower()
            
            if {'date', 'admissions'}.issubset(ad_df.columns):
                ad_df['date'] = pd.to_datetime(ad_df['date'])
                results['admissions'] = forecast_time_series(
                    ad_df, 'date', 'admissions', periods=30
                )
            else:
                return jsonify({'error': "Admissions CSV must have date and admissions columns."})
        except Exception as e:
            results['admissions'] = {'error': str(e)}
        
        
        try:
            demo_df = pd.read_csv(file_paths['demographics'])
            disc_df = pd.read_csv(file_paths['discharge'])
            
            demo_df.columns = demo_df.columns.str.lower()
            disc_df.columns = disc_df.columns.str.lower()
            
            required = {'patient_id', 'admission_date', 'discharge_date'}
            if not required.issubset(disc_df.columns):
                return jsonify({'error': "Discharge CSV must have patient_id, admission_date, discharge_date."})
            
            disc_df['admission_date'] = pd.to_datetime(disc_df['admission_date'])
            disc_df['discharge_date'] = pd.to_datetime(disc_df['discharge_date'])
            disc_df['los'] = (disc_df['discharge_date'] - disc_df['admission_date']).dt.days
            
            los_df = pd.merge(disc_df[['patient_id', 'los']], demo_df, on='patient_id')
            if 'gender' in los_df.columns:
                los_df['gender'] = los_df['gender'].map({'M': 0, 'F': 1}).fillna(0)
            
            features = [c for c in los_df.columns if c not in ('patient_id', 'los')]
            X = los_df[features]
            y = los_df['los']
            
            los_model = RandomForestRegressor(n_estimators=100, random_state=42)
            los_model.fit(X, y)
            
            avg_feat = X.mean().to_frame().T
            pred_avg_los = los_model.predict(avg_feat)[0]
            
            results['los'] = {
                'avg': float(pred_avg_los)
            }
        except Exception as e:
            results['los'] = {'error': str(e)}
        
        
        try:
            staff_df = pd.read_csv(file_paths['staff'])
            staff_df.columns = staff_df.columns.str.lower()
            
            if {'date', 'staff_count'}.issubset(staff_df.columns):
                staff_df['date'] = pd.to_datetime(staff_df['date'])
                
                
                admissions_forecast = results['admissions']['values']
                admissions_dates = [datetime.strptime(d, '%Y-%m-%d') for d in results['admissions']['dates']]
                
               
                avg_los = results['los']['avg']
                beds_needed = [np.ceil(a * avg_los) for a in admissions_forecast]
                
                
                ad_df['date'] = pd.to_datetime(ad_df['date'])
                hist = pd.merge(ad_df, staff_df, on='date', how='inner')
                avg_staff = hist['staff_count'].mean()
                avg_beds = hist['admissions'].mean() * avg_los
                ratio = avg_staff / avg_beds if avg_beds > 0 else 0.5
                staff_needed = [np.ceil(b * ratio) for b in beds_needed]
                
                
                plt.figure(figsize=(10, 6))
                plt.plot(admissions_dates, beds_needed, label='Beds Needed')
                plt.plot(admissions_dates, staff_needed, label='Staff Needed')
                plt.title('Bed & Staff Needs Forecast (Next 30 days)')
                plt.legend()
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                resources_chart = create_figure_to_base64(plt)
                
                results['resources'] = {
                    'chart': resources_chart,
                    'dates': results['admissions']['dates'],
                    'beds': beds_needed,
                    'staff': staff_needed
                }
            else:
                results['resources'] = {'error': "Staff CSV must have date and staff_count columns."}
        except Exception as e:
            results['resources'] = {'error': str(e)}
        
        
        try:
            icu_df = pd.read_csv(file_paths['icu'])
            icu_df.columns = icu_df.columns.str.lower()
            
            if 'date' not in icu_df.columns:
                return jsonify({'error': "ICU CSV must have a date column."})
            
            icu_df['date'] = pd.to_datetime(icu_df['date'])
            icu_results = {}
            
            for col in icu_df.columns:
                if col == 'date': 
                    continue
                
                icu_results[col] = forecast_time_series(icu_df, 'date', col, periods=30)
            
            results['icu'] = icu_results
        except Exception as e:
            results['icu'] = {'error': str(e)}
        
        
        if 'emergency' in file_paths:
            try:
                emer_df = pd.read_csv(file_paths['emergency'])
                emer_df.columns = emer_df.columns.str.lower()
                
                if {'date', 'emergency_cases'}.issubset(emer_df.columns):
                    emer_df['date'] = pd.to_datetime(emer_df['date'])
                    results['emergency'] = forecast_time_series(
                        emer_df, 'date', 'emergency_cases', periods=30
                    )
                else:
                    results['emergency'] = {'error': "Emergency CSV must have date and emergency_cases columns."}
            except Exception as e:
                results['emergency'] = {'error': str(e)}
        
        
        if 'department' in file_paths:
            try:
                dept_df = pd.read_csv(file_paths['department'])
                dept_df.columns = dept_df.columns.str.lower()
                
                if {'date', 'department', 'patient_count'}.issubset(dept_df.columns):
                    dept_df['date'] = pd.to_datetime(dept_df['date'])
                    departments = dept_df['department'].unique()
                    
                    dept_results = {}
                    
                    for dept in departments:
                        sub_df = dept_df[dept_df['department'] == dept][['date', 'patient_count']]
                        dept_results[dept] = forecast_time_series(
                            sub_df, 'date', 'patient_count', periods=30
                        )
                    
                    results['departments'] = dept_results
                else:
                    results['departments'] = {'error': "Department CSV must have date, department, and patient_count columns."}
            except Exception as e:
                results['departments'] = {'error': str(e)}
        
        
        for file_path in file_paths.values():
            try:
                os.remove(file_path)
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)