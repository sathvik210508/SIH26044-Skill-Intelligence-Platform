/**
 * SIH26044 — Chart.js Visualizations Wrapper (Light SaaS Theme)
 */

export const chartInstances = {};

export function destroyChart(canvasId) {
  if (chartInstances[canvasId]) {
    chartInstances[canvasId].destroy();
    delete chartInstances[canvasId];
  }
}

/**
 * Render Skill Gap Comparison Bar Chart
 */
export function renderSkillGapBar(canvasId, labels, currentVals, targetVals) {
  const ctx = document.getElementById(canvasId);
  if (!ctx || !window.Chart) return;
  destroyChart(canvasId);

  chartInstances[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Current Proficiency',
          data: currentVals,
          backgroundColor: '#4F46E5',
          borderRadius: 4
        },
        {
          label: 'Target Benchmark',
          data: targetVals,
          backgroundColor: '#E2E8F0',
          borderColor: '#CBD5E1',
          borderWidth: 1,
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          grid: { color: '#F1F5F9' },
          ticks: { color: '#64748B', font: { family: 'Inter', size: 11 } }
        },
        x: {
          grid: { display: false },
          ticks: { color: '#334155', font: { family: 'Inter', weight: '600', size: 11 } }
        }
      },
      plugins: {
        legend: {
          labels: { color: '#334155', font: { family: 'Inter', size: 12, weight: '500' } }
        }
      }
    }
  });
}

/**
 * Render National Supply vs Demand Bar Chart
 */
export function renderSupplyDemandBar(canvasId, labels, supplyVals, demandVals) {
  const ctx = document.getElementById(canvasId);
  if (!ctx || !window.Chart) return;
  destroyChart(canvasId);

  chartInstances[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Student Supply %',
          data: supplyVals,
          backgroundColor: '#16A34A',
          borderRadius: 4
        },
        {
          label: 'Industry Demand %',
          data: demandVals,
          backgroundColor: '#DC2626',
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          grid: { color: '#F1F5F9' },
          ticks: { color: '#64748B', font: { family: 'Inter', size: 11 } }
        },
        x: {
          grid: { display: false },
          ticks: { color: '#334155', font: { family: 'Inter', weight: '600', size: 11 } }
        }
      },
      plugins: {
        legend: {
          labels: { color: '#334155', font: { family: 'Inter', size: 12, weight: '500' } }
        }
      }
    }
  });
}

/**
 * Render Recruitment Funnel Bar Chart
 */
export function renderFunnelChart(canvasId, stages, values) {
  const ctx = document.getElementById(canvasId);
  if (!ctx || !window.Chart) return;
  destroyChart(canvasId);

  chartInstances[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: stages,
      datasets: [{
        label: 'Candidates',
        data: values,
        backgroundColor: [
          '#4F46E5',
          '#0284C7',
          '#D97706',
          '#16A34A'
        ],
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { color: '#F1F5F9' },
          ticks: { color: '#64748B', font: { family: 'Inter', size: 11 } }
        },
        y: {
          grid: { display: false },
          ticks: { color: '#334155', font: { family: 'Inter', weight: '600', size: 11 } }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}
