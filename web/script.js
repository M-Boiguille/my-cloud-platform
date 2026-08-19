async function loadMetrics() {
    try {
        const response = await fetch('metrics.json');
        const data = await response.json();

        document.getElementById('level').textContent = data.level;
        document.getElementById('target').textContent = data.target_level;
        document.getElementById('missions').textContent = data.missions_completed;
        document.getElementById('known').textContent = data.known_concepts_count;
        document.getElementById('upcoming').textContent = data.upcoming_concepts_count;
        document.getElementById('courses').textContent = data.active_courses.join(', ');

        const labels = Object.keys(data.skills);
        const values = Object.values(data.skills);

        const ctx = document.getElementById('skillsChart').getContext('2d');
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Compétences',
                    data: values,
                    backgroundColor: 'rgba(88, 166, 255, 0.2)',
                    borderColor: 'rgba(88, 166, 255, 1)',
                    pointBackgroundColor: 'rgba(88, 166, 255, 1)',
                    borderWidth: 2,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        min: 0,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            color: '#c9d1d9'
                        },
                        grid: {
                            color: '#30363d'
                        },
                        angleLines: {
                            color: '#30363d'
                        },
                        pointLabels: {
                            color: '#c9d1d9'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    } catch (error) {
        console.error('Impossible de charger metrics.json', error);
    }
}

loadMetrics();
