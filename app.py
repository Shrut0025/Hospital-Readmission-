from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
import joblib
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt

import seaborn as sns

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Load the model, scaler, and encoder
model = joblib.load('logistic_regression_model.pkl')
scaler = joblib.load('scaler.pkl')
encoder = joblib.load('onehot_encoder.pkl')



# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

@app.route('/')
def home():
    return render_template('home.html')

# Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid Credentials'
    return render_template('login.html')

# Dashboard Page
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Prediction Form Page
@app.route('/prediction')
def prediction():
    return render_template('patient_info.html')


@app.route('/patient_info', methods=['GET', 'POST'])
def patient_info():
    if request.method == 'POST':
        return predict()
    return render_template('patient_info.html')


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            # Collect form data
            data = {
                'age': int(request.form['age']),
                'gender': request.form['gender'],
                'condition': request.form['condition'],
                'procedure': request.form['procedure'],
                'time_in_hospital': int(request.form['time_in_hospital']),
                'blood_pressure': request.form['blood_pressure'],
                'freq_of_admission': int(request.form['freq_of_admission']),
                'glucose_test': request.form['glucose_test'],
                'smoking_alcohol_drug': request.form['smoking_alcohol_drug'],
                'outcome': request.form['outcome']
            }

            # Convert dictionary to DataFrame
            df = pd.DataFrame([data])

            # Perform one-hot encoding for categorical variables using the saved encoder
            df_encoded = encoder.transform(df[['gender', 'condition', 'procedure', 'blood_pressure', 'glucose_test', 'smoking_alcohol_drug', 'outcome']])

            # Convert encoded features to DataFrame
            df_encoded = pd.DataFrame(df_encoded, columns=encoder.get_feature_names_out())

            # Concatenate the numerical features with the encoded categorical features
            df_numerical = df.drop(columns=['gender', 'condition', 'procedure', 'blood_pressure', 'glucose_test', 'smoking_alcohol_drug', 'outcome'])
            df_final = pd.concat([df_numerical.reset_index(drop=True), df_encoded.reset_index(drop=True)], axis=1)

            # Scale the features using the loaded scaler
            input_scaled = scaler.transform(df_final)

            # Make prediction using the model
            prediction = model.predict(input_scaled)

            # Convert prediction to 'Yes' or 'No'
            result = 'Yes' if prediction[0] == 1 else 'No'

            # Store the patient info and prediction in the session
            session['patient_data'] = data
            session['patient_data']['readmitted'] = result

            # Use relative path assuming your CSV is in the same directory
            file_path = os.path.join(os.getcwd(), 'HOSPITAL_DATA_NEW.csv')

            # Add the prediction result to the DataFrame before saving
            df['readmitted'] = result

            # Append patient data to CSV
            df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)  # Write header only if file does not exist

            print(f"Data written to {file_path} successfully.")

            # Determine care recommendations based on prediction
            if result == "Yes":  # If readmission is needed
                care_recommendations = "Schedule a follow-up appointment and monitor the patient's condition closely."
            else:  # If readmission is not needed
                care_recommendations = "Regular check-ups are recommended to ensure ongoing recovery."

            return render_template('prediction_result.html', result=result, care_recommendations=care_recommendations)

        except Exception as e:
            return f"Error Occurred: {e}"

    return render_template('index.html')




def generate_analysis_charts(data):
    chart_paths = []
    
    # Create the 'static' directory if it doesn't exist
    os.makedirs('static', exist_ok=True)

    # 1. Pie chart of readmitted patients
    plt.figure(figsize=(10, 6))
    readmitted_counts = data['readmitted'].value_counts()
    plt.pie(readmitted_counts, labels=readmitted_counts.index, autopct='%1.1f%%', colors=['#ff9999','#66b3ff'])
    plt.title('Readmitted Patients')
    pie_chart_path = os.path.join('static', 'readmitted_pie_chart.png')
    plt.savefig(pie_chart_path)
    plt.close()
    chart_paths.append('readmitted_pie_chart.png')

    # 2. Box plot of time spent in hospital by gender
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='gender', y='time_in_hospital', data=data, palette=['#ff9999', '#66b3ff'])
    plt.title('Time in Hospital by Gender')
    plt.xlabel('Gender')
    plt.ylabel('Time in Hospital (hours)')
    time_in_hospital_gender_path = os.path.join('static', 'time_in_hospital_gender_boxplot.png')
    plt.savefig(time_in_hospital_gender_path)
    plt.close()
    chart_paths.append('time_in_hospital_gender_boxplot.png')

    # 3. Count Plot for Categorical Variable (Glucose Test Results)
    plt.figure(figsize=(10, 6))
    sns.countplot(x='glucose_test', data=data, palette='Set2')
    plt.title('Distribution of Glucose Test Results')
    plt.xlabel('Glucose Test Results')
    plt.ylabel('Count')
    glucose_test_path = os.path.join('static', 'glucose_test_distribution.png')
    plt.savefig(glucose_test_path)
    plt.close()
    chart_paths.append('glucose_test_distribution.png')

    # 4. Scatter plot of glucose test vs frequency of admission colored by outcome
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(data['glucose_test'], data['freq_of_admission'], c=pd.Categorical(data['outcome']).codes, cmap='coolwarm')
    plt.colorbar(scatter, ticks=[0, 1], label='Outcome (0: Recovered, 1: Stable)')
    plt.title('Glucose Test vs Frequency of Admission by Outcome')
    plt.xlabel('Glucose Test Levels')
    plt.ylabel('Frequency of Admission')
    glucose_freq_scatter_path = os.path.join('static', 'glucose_freq_scatter.png')
    plt.savefig(glucose_freq_scatter_path)
    plt.close()
    chart_paths.append('glucose_freq_scatter.png')

    # 5. plt.figure(figsize=(10, 6))
    sns.histplot(data['age'], kde=True, color='skyblue')
    plt.title('Age Distribution')
    plt.xlabel('Age')
    plt.ylabel('Frequency')
    age_distribution_path = os.path.join('static', 'age_distribution.png')
    plt.savefig(age_distribution_path)
    plt.close()
    chart_paths.append('age_distribution.png')

    # 6.Box Plot for Time in Hospital by Frequency of Admission
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='freq_of_admission', y='time_in_hospital', data=data)
    plt.title('Time in Hospital by Frequency of Admission')
    plt.xlabel('Frequency of Admission')
    plt.ylabel('Time in Hospital')
    boxplot_path = os.path.join('static', 'time_in_hospital_by_freq_of_admission.png')
    plt.savefig(boxplot_path)
    plt.close()
    chart_paths.append('time_in_hospital_by_freq_of_admission.png')


    return chart_paths

@app.route('/analysis')
def analysis():
    try:
        # Load data from CSV file
        file_path = os.path.abspath('HOSPITAL_DATA_NEW.csv')
        data = pd.read_csv(file_path)

        # Ensure necessary columns exist
        expected_columns = ['readmitted', 'age', 'time_in_hospital', 'condition']
        if not all(col in data.columns for col in expected_columns):
            return "Error: Required columns are missing from the data."

        # Convert 'readmitted' to numeric
        data['readmitted'] = data['readmitted'].map({'Yes': 1, 'No': 0})

        # Check for NaN values in crucial columns and drop or fill them as needed
        data.dropna(subset=['age', 'time_in_hospital', 'condition'], inplace=True)

        # Generate and save the charts
        chart_paths = generate_analysis_charts(data)

        # Pass the charts to the HTML template
        return render_template('analysis.html', chart_urls=chart_paths)
    except Exception as e:
        return f"Error Occurred: {e}"





@app.route('/get_chart_data', methods=['GET'])
def get_chart_data():
    # Load your CSV or database
    data = pd.read_csv('HOSPITAL_DATA_NEW.csv')

    # Age Distribution Data
    age_distribution = data['age'].value_counts().sort_index().tolist()

    # Readmission Rate by Condition
    readmission_condition = data.groupby('condition')['readmitted'].mean().tolist()

    # Impact of Blood Pressure
    blood_pressure_readmission = data.groupby('blood_pressure')['readmitted'].value_counts().unstack().fillna(0).to_dict()

    # Frequency of Admission vs. Readmission
    frequency_admission = data.groupby('freq_of_admission')['readmitted'].mean().tolist()

    # Outcome vs. Readmission
    outcome_readmission = data.groupby('outcome')['readmitted'].value_counts().unstack().fillna(0).to_dict()

    # Smoking/Alcohol/Drug Use
    smoking_alcohol_drug = data.groupby('smoking_alcohol_drug')['readmitted'].value_counts().unstack().fillna(0).to_dict()

    # Send JSON data to frontend
    return jsonify({
        'age_distribution': age_distribution,
        'readmission_condition': readmission_condition,
        'blood_pressure_readmission': blood_pressure_readmission,
        'frequency_admission': frequency_admission,
        'outcome_readmission': outcome_readmission,
        'smoking_alcohol_drug': smoking_alcohol_drug
    })




# Logout route (if applicable)
@app.route('/logout')
def logout():
    # Add your logout logic here if needed
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
