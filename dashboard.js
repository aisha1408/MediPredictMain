document.addEventListener('DOMContentLoaded', function() {
    const processBtn = document.getElementById('process-data');
    const forecastsDiv = document.getElementById('forecasts');
    
    
    let chartInstances = [];
    
 
    const files = {
        admissions: null,
        demographics: null,
        discharge: null,
        icu: null,
        staff: null,
        emergency: null,
        department: null
    };
    
    
    document.getElementById('admissions').addEventListener('change', (e) => {
        files.admissions = e.target.files[0];
    });
    
    document.getElementById('demographics').addEventListener('change', (e) => {
        files.demographics = e.target.files[0];
    });
    
    document.getElementById('discharge').addEventListener('change', (e) => {
        files.discharge = e.target.files[0];
    });
    
    document.getElementById('icu').addEventListener('change', (e) => {
        files.icu = e.target.files[0];
    });
    
    document.getElementById('staff').addEventListener('change', (e) => {
        files.staff = e.target.files[0];
    });
    
    document.getElementById('emergency').addEventListener('change', (e) => {
        files.emergency = e.target.files[0];
    });
    
    document.getElementById('department').addEventListener('change', (e) => {
        files.department = e.target.files[0];
    });
    
    
    processBtn.addEventListener('click', async () => {
        
        if (!files.admissions || !files.demographics || !files.discharge || !files.icu || !files.staff) {
            alert('Please upload all five core CSV files to proceed.');
            return;
        }
        
        
        forecastsDiv.innerHTML = '<div class="loading">Processing data... This may take a moment.</div>';
        
        
        const formData = new FormData();
        for (const [key, file] of Object.entries(files)) {
            if (file) {
                formData.append(key, file);
            }
        }
        
        try {
            
            const response = await fetch('/api/process-data', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.error) {
                forecastsDiv.innerHTML = `<div class="error">${data.error}</div>`;
                return;
            }
            
            
            renderForecasts(data);
            
        } catch (error) {
            console.error('Error:', error);
            forecastsDiv.innerHTML = '<div class="error">An error occurred while processing the data.</div>';
        }
    });
    
    
    function renderForecasts(data) {
        
        chartInstances.forEach(chart => {
            if (chart) chart.destroy();
        });
        chartInstances = [];
        
        let html = '';
        
        
        forecastsDiv.innerHTML = '';  

        
        html += `
            <section class="chart-container">
                <h2>1. Patient Admissions Forecast</h2>
                <p>Predicted daily patient admissions for the next 30 days</p>
                <canvas id="admissions-chart"></canvas>
            </section>
        `;
        
        
        html += `
            <section class="chart-container">
                <h2>2. Length‑of‑Stay (LOS) Prediction</h2>
                <div class="metric">
                    <h3>Predicted Avg LOS (days)</h3>
                    <div class="value">${data.los.avg.toFixed(2)}</div>
                </div>
            </section>
        `;
        
        
        html += `
            <section class="chart-container">
                <h2>3. Bed & Staff Needs (Next 30 days)</h2>
                <p>Forecasted resource requirements based on admissions and LOS</p>
                <canvas id="resources-chart"></canvas>
            </section>
        `;
        
        
        html += `
            <section class="chart-container">
                <h2>4. ICU Equipment Usage Forecast</h2>
                <div id="icu-charts"></div>
            </section>
        `;
        
        
        if (data.emergency && !data.emergency.error) {
            html += `
                <section class="chart-container">
                    <h2>5. Emergency Case Forecasting</h2>
                    <p>Predicted emergency cases for the next 30 days</p>
                    <canvas id="emergency-chart"></canvas>
                </section>
            `;
        }
        
        
        if (data.departments && !data.departments.error) {
            html += `
                <section class="chart-container">
                    <h2>6. Department-wise Patient Forecast</h2>
                    <div id="department-charts"></div>
                </section>
            `;
        }
        
        forecastsDiv.innerHTML = html; 
        
        
        createAdmissionsChart(data.admissions);
        createResourcesChart(data.resources);
        createICUCharts(data.icu);
        
        if (data.emergency && !data.emergency.error) {
            createEmergencyChart(data.emergency);
        }
        
        if (data.departments && !data.departments.error) {
            createDepartmentCharts(data.departments);
        }
    }
    
    function createAdmissionsChart(data) {
        const ctx = document.getElementById('admissions-chart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [{
                    label: 'Predicted Admissions',
                    data: data.values,
                    borderColor: 'rgba(78, 141, 242, 1)',
                    backgroundColor: 'rgba(78, 141, 242, 0.1)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        chartInstances.push(chart);
    }
    
    function createResourcesChart(data) {
        const ctx = document.getElementById('resources-chart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [{
                    label: 'Beds Needed',
                    data: data.beds,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    fill: true,
                    tension: 0.1
                }, {
                    label: 'Staff Needed',
                    data: data.staff,
                    borderColor: 'rgba(255, 159, 64, 1)',
                    backgroundColor: 'rgba(255, 159, 64, 0.1)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        chartInstances.push(chart);
    }
    
    function createICUCharts(icuData) {
        const icuChartsDiv = document.getElementById('icu-charts');
        let html = '';
        
       
        for (const [equipment, data] of Object.entries(icuData)) {
            if (data.error) continue;
            
            
            html += `
                <div class="icu-chart-item">
                    <h3>${equipment.replace(/_/g, ' ').toUpperCase()}</h3>
                    <canvas id="icu-chart-${equipment}"></canvas>
                </div>
            `;
        }
        
        icuChartsDiv.innerHTML = html;
        
        
        for (const [equipment, data] of Object.entries(icuData)) {
            if (data.error) continue;
            
            const canvas = document.getElementById(`icu-chart-${equipment}`);
            if (!canvas) continue;
            
            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.dates,
                    datasets: [{
                        label: `Predicted ${equipment.replace(/_/g, ' ')}`,
                        data: data.values,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        fill: true,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            chartInstances.push(chart);
        }
    }
    
    function createEmergencyChart(data) {
        const ctx = document.getElementById('emergency-chart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [{
                    label: 'Predicted Emergency Cases',
                    data: data.values,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        chartInstances.push(chart);
    }
    
    function createDepartmentCharts(departmentsData) {
        const deptChartsDiv = document.getElementById('department-charts');
        let html = '';
        
        
        for (const [dept, data] of Object.entries(departmentsData)) {
            if (data.error) continue;
            
            
            html += `
                <div class="dept-chart-item">
                    <h3>${dept.charAt(0).toUpperCase() + dept.slice(1)} Department</h3>
                    <canvas id="dept-chart-${dept}"></canvas>
                </div>
            `;
        }
        
        deptChartsDiv.innerHTML = html;
        
        
        for (const [dept, data] of Object.entries(departmentsData)) {
            if (data.error) continue;
            
            const canvas = document.getElementById(`dept-chart-${dept}`);
            if (!canvas) continue;
            
            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.dates,
                    datasets: [{
                        label: `Predicted Patients`,
                        data: data.values,
                        borderColor: 'rgba(153, 102, 255, 1)',
                        backgroundColor: 'rgba(153, 102, 255, 0.1)',
                        fill: true,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            chartInstances.push(chart);
        }
    }
});