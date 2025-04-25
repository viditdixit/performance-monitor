// Default polling interval (5 seconds)
let interval = 5000;
let intervalID;

// Function to display errors non-intrusively
function displayError(message) {
    // You could create a dedicated error div in your HTML
    // For now, let's use console.error and maybe update a status area
    console.error(message);
    const statusDiv = document.getElementById('status-message'); // Need to add this div to HTML
    if (statusDiv) {
        statusDiv.textContent = `Error: ${message}`;
        statusDiv.className = 'status error'; // Add an error class for styling
    }
    // Avoid using alert() as it blocks the UI
    // alert('Failed to update system metrics. Please check console.');
}

// Function to update the anomaly status display
function updateAnomalyStatus(isAnomaly) {
    const statusDiv = document.getElementById('status-message'); // Use the same div
    if (statusDiv) {
        if (isAnomaly) {
            statusDiv.textContent = '🚨 Anomaly Detected! Please check the system immediately!';
            statusDiv.className = 'status alert'; // Use 'alert' class from CSS
        } else {
            statusDiv.textContent = '✅ System is running smoothly.';
            statusDiv.className = 'status safe'; // Use 'safe' class from CSS
        }
    }
}


// Function to fetch updated metrics and update the dashboard
function updateMetrics() {
    fetch('/metrics')
        .then(response => {
            if (!response.ok) {
                // Throw an error with status text if available
                throw new Error(`Network response was not ok: ${response.statusText} (status: ${response.status})`);
            }
            return response.json(); // Parse JSON data
        })
        .then(data => {
            // Check if data contains an error message from the server
            if (data.error) {
                 throw new Error(`Server error: ${data.error}`);
            }

            // Update metric values
            document.getElementById('cpu').innerText = data.cpu_usage.toFixed(2) + '%'; // Format to 2 decimal places
            document.getElementById('memory').innerText = data.memory_usage.toFixed(2) + '%';
            document.getElementById('load').innerText = data.load_avg.toFixed(2);

            // Update anomaly status display
            updateAnomalyStatus(data.anomaly_detected);

            // Update chart data
            updateChart(data.cpu_usage, data.memory_usage, data.load_avg);
        })
        .catch(error => {
            // Display the error non-intrusively
            displayError(`Failed to fetch or process metrics: ${error.message}`);
            // Optionally, clear or reset parts of the UI here if desired
        });
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
                borderColor: '#ff6384', // Consider softer colors?
                backgroundColor: 'rgba(255, 99, 132, 0.1)', // Slight fill might look nice
                fill: true, // Set fill to true or false
                tension: 0.1 // Slight curve to lines
            },
            {
                label: 'Memory Usage (%)',
                data: [],
                borderColor: '#36a2eb',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                fill: true,
                tension: 0.1
            },
            {
                label: 'Load Avg',
                data: [],
                borderColor: '#4bc0c0',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                fill: true,
                tension: 0.1
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false, // Allow chart to resize height independently
        scales: {
            x: {
                display: true,
                title: { display: true, text: 'Time' }
            },
            y: {
                display: true,
                title: { display: true, text: 'Value' },
                beginAtZero: true, // Start Y axis at 0
                suggestedMax: 100 // Suggest 100 for percentage axes if appropriate
            }
        },
        animation: {
            duration: 200 // Faster animation for smoother updates
        }
    }
});

// Function to update chart dynamically
function updateChart(cpu, memory, load) {
    let now = new Date().toLocaleTimeString(); // HH:MM:SS format

    // Limit the number of data points shown on the chart
    const maxDataPoints = 30; // Show last 30 data points (adjust as needed)
    if (metricsChart.data.labels.length >= maxDataPoints) {
        metricsChart.data.labels.shift(); // Remove oldest label
        metricsChart.data.datasets.forEach(dataset => {
            dataset.data.shift(); // Remove oldest data point for each dataset
        });
    }

    // Add new data
    metricsChart.data.labels.push(now);
    metricsChart.data.datasets[0].data.push(cpu);
    metricsChart.data.datasets[1].data.push(memory);
    metricsChart.data.datasets[2].data.push(load);

    // Update the chart without full redraw animation if possible
    metricsChart.update('none'); // Use 'none' or a small duration for less disruptive updates
}

// Function to start polling with the selected interval
function startPolling() {
    if (intervalID) {
        clearInterval(intervalID); // Clear existing interval if any
    }
    updateMetrics(); // Fetch immediately when interval changes or page loads
    intervalID = setInterval(updateMetrics, interval); // Start new interval
    console.log(`Polling interval set to ${interval / 1000} seconds.`);
}

// Event listener for dropdown selection and initial load
document.addEventListener("DOMContentLoaded", function () {
    // Listener for interval change
    document.getElementById("interval-select").addEventListener("change", function (event) {
        const selectedInterval = parseInt(event.target.value, 10); // Base 10
        if (!isNaN(selectedInterval) && selectedInterval > 0) {
             interval = selectedInterval * 1000; // Convert seconds to milliseconds
             startPolling(); // Restart polling with new interval
        } else {
            console.error("Invalid interval selected:", event.target.value);
        }
    });

    // Initial call to start polling
    startPolling();
});