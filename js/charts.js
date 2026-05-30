/**
 * Charts Visualization Manager (charts.js)
 * Visualizes AI engine metrics including search comparative latencies,
 * nodes expanded, utility values, and Bayesian probability distributions.
 */

let searchChartInstance = null;
let utilityChartInstance = null;
let bayesChartInstance = null;

const ChartsManager = {
    // 1. Draw Search Algorithms Performance Comparison (CO2)
    drawSearchComparison: function(comparisons) {
        const ctx = document.getElementById('searchChart');
        if (!ctx) return;
        
        if (searchChartInstance) {
            searchChartInstance.destroy();
        }
        
        const labels = comparisons.map(c => c.algorithm);
        const latencies = comparisons.map(c => c.execution_time_ms);
        const nodesExpanded = comparisons.map(c => c.nodes_expanded);
        
        searchChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Execution Latency (ms)',
                        data: latencies,
                        backgroundColor: 'rgba(99, 102, 241, 0.6)',
                        borderColor: '#6366f1',
                        borderWidth: 1.5,
                        yAxisID: 'y-latency'
                    },
                    {
                        label: 'Nodes Expanded',
                        data: nodesExpanded,
                        backgroundColor: 'rgba(236, 72, 153, 0.6)',
                        borderColor: '#ec4899',
                        borderWidth: 1.5,
                        yAxisID: 'y-nodes'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#e5e7eb', font: { family: 'Outfit', size: 12 } }
                    },
                    tooltip: {
                        backgroundColor: '#0f172a',
                        titleColor: '#f3f4f6',
                        bodyColor: '#9ca3af',
                        borderColor: 'rgba(99, 102, 241, 0.3)',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af', font: { family: 'Outfit' } }
                    },
                    'y-latency': {
                        type: 'linear',
                        position: 'left',
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af', font: { family: 'Outfit' } },
                        title: {
                            display: true,
                            text: 'Latency (Milliseconds)',
                            color: '#6366f1',
                            font: { family: 'Outfit', weight: 'bold' }
                        }
                    },
                    'y-nodes': {
                        type: 'linear',
                        position: 'right',
                        grid: { display: false },
                        ticks: { color: '#9ca3af', font: { family: 'Outfit' } },
                        title: {
                            display: true,
                            text: 'Search Nodes Expanded',
                            color: '#ec4899',
                            font: { family: 'Outfit', weight: 'bold' }
                        }
                    }
                }
            }
        });
    },

    // 2. Draw Multi-Attribute Utility (MAUT) Breakdown (CO4)
    drawUtilityBreakdown: function(recommendations) {
        const ctx = document.getElementById('utilityChart');
        if (!ctx) return;

        if (utilityChartInstance) {
            utilityChartInstance.destroy();
        }

        // Limit to top 4 recommendations for visual clarity
        const items = recommendations.slice(0, 4);
        const labels = items.map(r => r.code);
        
        const interestData = items.map(r => r.utility_breakdown.interest * 100);
        const skillData = items.map(r => r.utility_breakdown.skills * 100);
        const careerData = items.map(r => r.utility_breakdown.career * 100);
        const diffData = items.map(r => r.utility_breakdown.difficulty * 100);

        utilityChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    { label: 'Interest Match (40%)', data: interestData, backgroundColor: 'rgba(99, 102, 241, 0.7)' },
                    { label: 'Skill Match (25%)', data: skillData, backgroundColor: 'rgba(168, 85, 247, 0.7)' },
                    { label: 'Career Fit (25%)', data: careerData, backgroundColor: 'rgba(6, 182, 212, 0.7)' },
                    { label: 'Difficulty Alignment (10%)', data: diffData, backgroundColor: 'rgba(245, 158, 11, 0.7)' }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#e5e7eb', font: { family: 'Outfit' } }
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af', font: { family: 'Outfit' } }
                    },
                    y: {
                        stacked: true,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: '#9ca3af', font: { family: 'Outfit' } },
                        title: {
                            display: true,
                            text: 'Stacked Attribute Weight (%)',
                            color: '#e5e7eb',
                            font: { family: 'Outfit' }
                        }
                    }
                }
            }
        });
    },

    // 3. Draw Bayesian Node Prior Distributions (CO5)
    drawBayesianDistribution: function(topCourse) {
        const ctx = document.getElementById('bayesChart');
        if (!ctx) return;

        if (bayesChartInstance) {
            bayesChartInstance.destroy();
        }

        const priors = topCourse.evidence_priors;
        const confidence = topCourse.confidence_score;

        bayesChartInstance = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: [
                    'Interest Fit Prior P(I=1)', 
                    'Background Strengths P(B=1)', 
                    'Course Complexity Prior P(D=1)', 
                    'Overall Success Confidence P(S=1)'
                ],
                datasets: [{
                    label: `Probability Analysis for ${topCourse.code}`,
                    data: [priors.interest_fit, priors.background_pass, priors.difficulty_high, confidence],
                    backgroundColor: 'rgba(168, 85, 247, 0.2)',
                    borderColor: '#a855f7',
                    pointBackgroundColor: '#ec4899',
                    pointBorderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#e5e7eb', font: { family: 'Outfit' } }
                    }
                },
                scales: {
                    r: {
                        grid: { color: 'rgba(255, 255, 255, 0.08)' },
                        angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
                        ticks: { backdropColor: 'transparent', color: '#9ca3af', font: { family: 'Outfit' } },
                        pointLabels: { color: '#9ca3af', font: { family: 'Outfit', size: 10 } },
                        min: 0,
                        max: 100
                    }
                }
            }
        });
    }
};