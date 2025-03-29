// Default polling interval (5 seconds)
let interval = 5000;
let intervalID;

// Function to fetch updated metrics and update the dashboard
function updateMetrics() {
    fetch('/metrics')
        .then(response => response.json())
        .then(data => {
            document.getElementById('cpu').innerText = data.cpu_usage + '%';
            document.getElementById('memory').innerText = data.memory_usage + '%';
            document.getElementById('load').innerText = data.load_avg;

            // Update chart data
            updateChart(data.cpu_usage, data.memory_usage, data.load_avg);
        })
        .catch(error => console.error('Error fetching data:', error));
}

// Initialize Chart.js
let ctx = document.getElementById('metricsChart').getContext('2d');
let metricsChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [], // Time labels
        datasets: [
            {
                label: 'CPU Usage (%)',
                data: [],
                borderColor: '#ff6384',
                fill: false
            },
            {
                label: 'Memory Usage (%)',
                data: [],
                borderColor: '#36a2eb',
                fill: false
            },
            {
                label: 'Load Avg',
                data: [],
                borderColor: '#4bc0c0',
                fill: false
            }
        ]
    },
    options: {
        responsive: true,
        scales: {
            x: { display: true, title: { display: true, text: 'Time' } },
            y: { display: true, title: { display: true, text: 'Value' } }
        }
    }
});

// Function to update chart dynamically
function updateChart(cpu, memory, load) {
    let now = new Date().toLocaleTimeString();
    if (metricsChart.data.labels.length > 20) {
        metricsChart.data.labels.shift();
        metricsChart.data.datasets.forEach(dataset => dataset.data.shift());
    }
    metricsChart.data.labels.push(now);
    metricsChart.data.datasets[0].data.push(cpu);
    metricsChart.data.datasets[1].data.push(memory);
    metricsChart.data.datasets[2].data.push(load);
    metricsChart.update();
}

// Function to start polling with the selected interval
function startPolling() {
    if (intervalID) clearInterval(intervalID);
    updateMetrics(); // Fetch immediately
    intervalID = setInterval(updateMetrics, interval);
}

// Event listener for dropdown selection
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("interval-select").addEventListener("change", function (event) {
        interval = parseInt(event.target.value) * 1000; // Convert seconds to milliseconds
        startPolling();
    });

    startPolling(); // Start polling initially
});
