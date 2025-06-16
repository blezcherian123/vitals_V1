// Placeholder for future interactivity (e.g., filtering, sorting patients)
console.log('Doctor Dashboard loaded.');

// Initialize Bootstrap modal
const historyModal = new bootstrap.Modal(document.getElementById('historyModal'));

// Search and filter functionality
document.getElementById('searchInput').addEventListener('input', filterPatients);
document.getElementById('filterStatus').addEventListener('change', filterPatients);
document.getElementById('sortBy').addEventListener('change', sortPatients);

function filterPatients() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('filterStatus').value;
    const patientCards = document.querySelectorAll('.patient-card');

    patientCards.forEach(card => {
        const patientName = card.querySelector('h3').textContent.toLowerCase();
        const patientStatus = card.dataset.status;
        const matchesSearch = patientName.includes(searchTerm);
        const matchesStatus = statusFilter === 'all' || patientStatus === statusFilter;

        card.closest('.col-md-6').style.display = matchesSearch && matchesStatus ? 'block' : 'none';
    });
}

function sortPatients() {
    const sortBy = document.getElementById('sortBy').value;
    const patientList = document.getElementById('patient-list');
    const patientCards = Array.from(patientList.getElementsByClassName('col-md-6'));

    patientCards.sort((a, b) => {
        const cardA = a.querySelector('.patient-card');
        const cardB = b.querySelector('.patient-card');

        switch (sortBy) {
            case 'name':
                return cardA.querySelector('h3').textContent.localeCompare(cardB.querySelector('h3').textContent);
            case 'critical':
                return cardB.dataset.status.localeCompare(cardA.dataset.status);
            case 'recent':
            default:
                const dateA = new Date(cardA.querySelector('.vital-signs p:last-child').textContent.split(': ')[1]);
                const dateB = new Date(cardB.querySelector('.vital-signs p:last-child').textContent.split(': ')[1]);
                return dateB - dateA;
        }
    });

    patientCards.forEach(card => patientList.appendChild(card));
}

// View patient history
function viewPatientHistory(registrationId) {
    fetch(`/patient_history/${registrationId}`)
        .then(response => response.json())
        .then(history => {
            const historyContent = document.getElementById('historyContent');
            historyContent.innerHTML = '';

            if (history.error) {
                historyContent.innerHTML = `<div class="alert alert-danger">${history.error}</div>`;
                return;
            }

            const table = document.createElement('table');
            table.className = 'table table-striped';
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Time</th>
                        <th>BMI</th>
                        <th>BP</th>
                        <th>Temp</th>
                        <th>Pulse</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${history.map(record => `
                        <tr>
                            <td>${record.date}</td>
                            <td>${record.time}</td>
                            <td>${record.bmi}</td>
                            <td>${record.systolic_bp}/${record.diastolic_bp}</td>
                            <td>${record.temp}°F</td>
                            <td>${record.pulse}</td>
                            <td>
                                <span class="badge ${record.alerts.includes('Critical Alert') ? 'bg-danger' : 
                                    record.alerts ? 'bg-warning' : 'bg-success'}">
                                    ${record.alerts.includes('Critical Alert') ? 'Critical' : 
                                    record.alerts ? 'Warning' : 'Normal'}
                                </span>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            `;

            historyContent.appendChild(table);
            historyModal.show();
        })
        .catch(error => {
            console.error('Error fetching patient history:', error);
            document.getElementById('historyContent').innerHTML = 
                '<div class="alert alert-danger">Error loading patient history</div>';
            historyModal.show();
        });
}

// Auto-refresh dashboard every 5 minutes
setInterval(() => {
    window.location.reload();
}, 300000);

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});