// Fetch data from the Flask endpoint
fetch('/get_chart_data')
    .then(response => response.json())
    .then(data => {
        if (!data) {
            console.error('No data received');
            return;
        }

        // 1. Age Distribution of Patients
        const ageCtx = document.getElementById('ageDistributionChart').getContext('2d');
        new Chart(ageCtx, {
            type: 'bar',
            data: {
                labels: [...Array(data.age_distribution.length).keys()],  // Age labels
                datasets: [{
                    label: 'Number of Patients',
                    data: data.age_distribution,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // 2. Readmission Rate by Condition
        const conditionCtx = document.getElementById('readmissionRateConditionChart').getContext('2d');
        new Chart(conditionCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(data.readmission_condition),  // Conditions
                datasets: [{
                    label: 'Readmission Rate',
                    data: Object.values(data.readmission_condition), // Ensure you're getting values
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // 3. Impact of Blood Pressure on Readmission
        const bpCtx = document.getElementById('bloodPressureReadmissionChart').getContext('2d');
        new Chart(bpCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(data.blood_pressure_readmission),
                datasets: [{
                    label: 'Not Readmitted',
                    data: Object.values(data.blood_pressure_readmission).map(val => val[0]),  // Not readmitted
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }, {
                    label: 'Readmitted',
                    data: Object.values(data.blood_pressure_readmission).map(val => val[1]),  // Readmitted
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // 4. Frequency of Admission vs. Readmission
        const freqCtx = document.getElementById('frequencyAdmissionReadmissionChart').getContext('2d');
        new Chart(freqCtx, {
            type: 'line',
            data: {
                labels: [...Array(data.frequency_admission.length).keys()],
                datasets: [{
                    label: 'Readmission Probability',
                    data: data.frequency_admission,
                    backgroundColor: 'rgba(255, 206, 86, 0.2)',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // 5. Outcome vs. Readmission
        const outcomeCtx = document.getElementById('outcomeReadmissionChart').getContext('2d');
        new Chart(outcomeCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(data.outcome_readmission),
                datasets: [{
                    label: 'Not Readmitted',
                    data: Object.values(data.outcome_readmission).map(val => val[0]),
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }, {
                    label: 'Readmitted',
                    data: Object.values(data.outcome_readmission).map(val => val[1]),
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // 6. Smoking/Alcohol/Drug Use vs. Readmission
        const sadCtx = document.getElementById('smokingAlcoholDrugChart').getContext('2d');
        new Chart(sadCtx, {
            type: 'pie',
            data: {
                labels: Object.keys(data.smoking_alcohol_drug),
                datasets: [{
                    label: 'Readmission',
                    data: Object.values(data.smoking_alcohol_drug).map(val => val[1]),
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true
            }
        });
    })
    .catch(error => console.error('Error fetching chart data:', error));
