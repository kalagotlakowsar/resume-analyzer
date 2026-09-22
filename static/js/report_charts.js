/* ===================================================================
   AI Resume Analyzer - Report Visualizations & Charts
   =================================================================== */

function initReportVisuals(subscoresData, skillsDistData, overallAtsScore) {
    // 1. Animate Circular Progress Gauge
    const circle = document.querySelector('.score-circle-progress');
    if (circle) {
        const radius = 70;
        const circumference = 2 * Math.PI * radius;
        circle.style.strokeDasharray = `${circumference} ${circumference}`;
        circle.style.strokeDashoffset = `${circumference}`;

        const offset = circumference - ((overallAtsScore / 100) * circumference);
        setTimeout(() => {
            circle.style.strokeDashoffset = offset;
            // Color according to score
            if (overallAtsScore >= 85) {
                circle.style.stroke = '#10b981'; // Green
            } else if (overallAtsScore >= 70) {
                circle.style.stroke = '#3b82f6'; // Blue
            } else if (overallAtsScore >= 50) {
                circle.style.stroke = '#f59e0b'; // Amber
            } else {
                circle.style.stroke = '#ef4444'; // Red
            }
        }, 200);
    }

    // 2. Subscores Radar Chart
    const radarCtx = document.getElementById('subscoresRadarChart');
    if (radarCtx && subscoresData) {
        new Chart(radarCtx, {
            type: 'radar',
            data: {
                labels: subscoresData.labels,
                datasets: [{
                    label: 'Score Profile (0-100)',
                    data: subscoresData.values,
                    backgroundColor: 'rgba(79, 70, 229, 0.2)',
                    borderColor: '#4f46e5',
                    borderWidth: 2,
                    pointBackgroundColor: '#4f46e5',
                    pointBorderColor: '#ffffff',
                    pointHoverBackgroundColor: '#ffffff',
                    pointHoverBorderColor: '#4f46e5',
                    pointRadius: 4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: 'rgba(0, 0, 0, 0.08)' },
                        grid: { color: 'rgba(0, 0, 0, 0.08)' },
                        suggestedMin: 0,
                        suggestedMax: 100,
                        ticks: { stepSize: 20, display: false }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // 3. Skills Gap Distribution Doughnut Chart
    const distCtx = document.getElementById('skillsDistChart');
    if (distCtx && skillsDistData) {
        new Chart(distCtx, {
            type: 'doughnut',
            data: {
                labels: skillsDistData.labels,
                datasets: [{
                    data: skillsDistData.values,
                    backgroundColor: ['#10b981', '#ef4444', '#0284c7'],
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            padding: 15,
                            font: { family: 'Plus Jakarta Sans', size: 12 }
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }
}
