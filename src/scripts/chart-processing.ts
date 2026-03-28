import Chart, { type TooltipItem } from 'chart.js/auto';
const svgEye = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>`;
const svgEyeOff = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/></svg>`;

const containers = document.querySelectorAll('.banana-chart-container');

containers.forEach(container => {
  const dataNode = container.getElementsByClassName('banana-chart-data')?.item(0) as HTMLSpanElement;

  if (!dataNode?.dataset) {
    console.log("Missing data", container);
    return;
  }

  const type = dataNode.dataset.type as string;
  const labels = JSON.parse(dataNode.dataset.labels ?? '[]') as string[];

  if (type === 'rice-index') {
    const lineId = dataNode.dataset.chart;
    const gaugeId = dataNode.dataset.legend;
    const overallVal = Number(dataNode.dataset.gaugeVal || 0);
    const lineData = JSON.parse(dataNode.dataset.data ?? '[]') as number[];
    
    if (!lineId || !gaugeId) return;
    const lineCanvas = document.getElementById(lineId) as HTMLCanvasElement;
    const gaugeCanvas = document.getElementById(gaugeId) as HTMLCanvasElement;
    if (!lineCanvas || !gaugeCanvas) return;

    // Gauge Chart initialization
    new Chart(gaugeCanvas, {
      type: 'doughnut',
      data: {
        labels: ['Cohesión', 'División'],
        datasets: [{
          data: [overallVal, Math.max(0, 100 - overallVal)],
          backgroundColor: ['#00b2e3', 'rgba(139, 148, 158, 0.15)'],
          borderWidth: 0,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '75%',
        circumference: 180,
        rotation: 270,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false }
        }
      }
    });

    // Line Chart initialization
    new Chart(lineCanvas, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Índice de Cohesión',
          data: lineData,
          borderColor: '#00b2e3',
          backgroundColor: 'rgba(0, 178, 227, 0.1)',
          borderWidth: 2,
          pointBackgroundColor: '#00b2e3',
          pointRadius: 4,
          pointHoverRadius: 6,
          fill: true,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            padding: 12,
            callbacks: {
              label: function(context: TooltipItem<'line'>) { return `${(context.parsed.y || 0).toFixed(1)}%`; }
            }
          }
        },
        scales: {
          x: { grid: { display: false } },
          y: { 
            min: 0, 
            max: 100, 
            grid: { color: 'rgba(139, 148, 158, 0.1)' } 
          }
        }
      }
    });

    return; // Exit early since we handled rice-index
  }

  const chartId = dataNode.dataset.chart;
  const legendId = dataNode.dataset.legend;

  if (!type || !labels || !chartId || !legendId) return;

  const canvas = document.getElementById(chartId) as HTMLCanvasElement;
  const legendContainer = document.getElementById(legendId) as HTMLDivElement;

  if (!canvas || !legendContainer) return;

  const basePalette = ['#00b2e3', '#00da9f', '#ffd700', '#ff6b6b', '#9b59b6', '#f39c12', '#e74c3c', '#34495e', '#2ecc71', '#e67e22'];

  if (type === 'donut') {
    const data = JSON.parse(dataNode.dataset.data ?? '[]') as number[];
    if (!data || data.length != labels.length) return;

    const chartColors = data.map((_, i) => basePalette[i % basePalette.length]);

    const chart = new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: chartColors,
          borderWidth: 0,
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            padding: 12,
            callbacks: {
              label: doughnutTooltipLabel
            }
          }
        }
      }
    });

    renderDoughnutLegend(chart, legendContainer);
  } else if (type === 'stacked-bar') {
    const datasetsConfig = JSON.parse(dataNode.dataset.datasets || '[]') as {label: string, data: number[]}[];
    if (!datasetsConfig || datasetsConfig.length === 0) return;

    const chartColors = datasetsConfig.map((_, i) => basePalette[i % basePalette.length]);

    const chart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels,
        datasets: datasetsConfig.map((ds, idx) => ({
          label: ds.label,
          data: ds.data,
          backgroundColor: chartColors[idx]
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: { label: stackedTooltipLabel }
          }
        },
        scales: {
          x: { stacked: true, grid: { color: 'rgba(139, 148, 158, 0.1)' } },
          y: { stacked: true, grid: { color: 'rgba(139, 148, 158, 0.1)' } }
        }
      }
    });
    
    renderBarLegend(chart, legendId, labels);
  } else if (type === 'line') {
    const datasetsConfig = JSON.parse(dataNode.dataset.datasets || '[]') as {label: string, data: number[]}[];
    if (!datasetsConfig || datasetsConfig.length === 0) return;

    const customColors = dataNode.dataset.colors ? JSON.parse(dataNode.dataset.colors) as string[] : null;
    const chartColors = customColors && customColors.length > 0
      ? datasetsConfig.map((_, i) => customColors[i % customColors.length])
      : datasetsConfig.map((_, i) => basePalette[i % basePalette.length]);
    const yMax = dataNode.dataset.yMax ? Number(dataNode.dataset.yMax) : undefined;

    const chart = new Chart(canvas, {
      type: 'line',
      data: {
        labels,
        datasets: datasetsConfig.map((ds, idx) => ({
          label: ds.label,
          data: ds.data,
          borderColor: chartColors[idx],
          backgroundColor: chartColors[idx] + '22',
          borderWidth: 2,
          pointBackgroundColor: chartColors[idx],
          pointRadius: 3,
          pointHoverRadius: 5,
          fill: true,
          tension: 0.3
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            padding: 12,
            callbacks: {
              label: (context: TooltipItem<'line'>) => `${context.dataset.label}: ${context.parsed.y}`
            }
          }
        },
        scales: {
          x: { grid: { color: 'rgba(139, 148, 158, 0.1)' } },
          y: {
            min: 0,
            max: yMax,
            grid: { color: 'rgba(139, 148, 158, 0.1)' }
          }
        }
      }
    });

    renderLineLegend(chart, legendContainer, chartColors);
  }
});


function doughnutTooltipLabel(context: TooltipItem<'doughnut'>) {
  const value = Number(context.parsed || 0);
  return `${context.label}: ${value}`;
}

function stackedTooltipLabel(context: TooltipItem<'bar'>) {
  const value = Number(context.parsed?.y ?? context.parsed ?? 0);
  const dataIndex = context.dataIndex;
  const datasets = context.chart?.data?.datasets || [];
  const total = datasets.reduce((sum, ds) => sum + Number((ds.data || [])[dataIndex] || 0), 0);
  const formatPercent = (val: number, tot: number) => (tot > 0 ? ((val / tot) * 100).toFixed(1) : '0.0');
  return `${context.dataset.label}: ${value} (${formatPercent(value, total)}%)`;
}

function renderDoughnutLegend(chart: Chart<'doughnut'>, container: HTMLDivElement) {
  const labels = (chart.data.labels ?? []).map(label => String(label));
  const dataset = chart.data.datasets[0];
  if (!dataset) {
    container.innerHTML = '';
    return;
  }

  const values = (dataset.data ?? []).map(value => Number(value || 0));
  const bg = dataset.backgroundColor;
  const colors = Array.isArray(bg) ?
    bg.map(color => String(color)) :
    labels.map(() => String(bg || '#8b949e'));
  const visibleTotal = values.reduce((sum, value, index) => (
    chart.getDataVisibility(index) ? sum + value : sum
  ), 0);

  const list = document.createElement('div');
  list.className = 'custom-legend-list';

  labels.forEach((label, index) => {
    const isVisible = chart.getDataVisibility(index);

    const item = document.createElement('div');
    item.className = 'custom-legend-item';
    if (!isVisible) item.classList.add('is-hidden');
    item.tabIndex = 0;
    item.setAttribute('role', 'button');
    item.setAttribute('aria-pressed', isVisible ? 'true' : 'false');

    const onToggle = () => {
      chart.toggleDataVisibility(index);
      chart.update();
      renderDoughnutLegend(chart, container);
    };

    item.addEventListener('click', onToggle);
    item.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        onToggle();
      }
    });

    // Color Square
    const colorBox = document.createElement('div');
    colorBox.className = 'legend-color-square';
    colorBox.style.backgroundColor = colors[index] || '#8b949e';
    item.appendChild(colorBox);

    // Label & Data wrapper
    const infoWrap = document.createElement('div');
    infoWrap.className = 'legend-info-wrap';

    const labelEl = document.createElement('div');
    labelEl.className = 'legend-title';
    labelEl.textContent = label;

    const valueEl = document.createElement('div');
    valueEl.className = 'legend-stats';
    const actualValue = values[index] || 0;
    const pct = isVisible ? visibleTotal > 0 ? ((actualValue / visibleTotal) * 100).toFixed(1) : '0.0' : '0.0';
    valueEl.innerHTML = `<span class="val-count">${actualValue}</span> <span class="val-pct">(${pct}%)</span>`;

    infoWrap.appendChild(labelEl);
    infoWrap.appendChild(valueEl);
    item.appendChild(infoWrap);

    // Eye Icon
    const iconWrap = document.createElement('div');
    iconWrap.className = 'legend-eye-icon';
    iconWrap.innerHTML = isVisible ? svgEye : svgEyeOff;
    item.appendChild(iconWrap);

    list.appendChild(item);
  });

  container.replaceChildren(list);
}

function renderBarLegend(chart: Chart<'bar'>, containerId: string, periods: string[]) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const datasets = chart.data.datasets;
  if (!datasets || datasets.length === 0) {
    container.innerHTML = '';
    return;
  }

  const visiblePeriodTotals = periods.map((_, pIndex) => {
    return datasets.reduce((sum, ds, dIndex) => {
      const meta = chart.getDatasetMeta(dIndex);
      const isVisible = meta.hidden === null || !meta.hidden;
      return sum + (isVisible ? Number((ds.data || [])[pIndex] || 0) : 0);
    }, 0);
  });

  const list = document.createElement('div');
  list.className = 'period-legend-list';

  periods.forEach((period, pIndex) => {
    const pCard = document.createElement('div');
    pCard.className = 'period-legend-card glass-panel';

    const pHeader = document.createElement('div');
    pHeader.className = 'period-legend-header';
    pHeader.innerHTML = `<h4>${period}</h4> <span class="period-total-badge">${visiblePeriodTotals[pIndex]} total</span>`;
    pCard.appendChild(pHeader);

    const pItems = document.createElement('div');
    pItems.className = 'custom-legend-list';

    datasets.forEach((dataset, dIndex) => {
      const meta = chart.getDatasetMeta(dIndex);
      const isVisible = meta.hidden === null || !meta.hidden;
      const label = String(dataset.label || `Dataset ${dIndex}`);
      const bg = dataset.backgroundColor;
      const color = String(Array.isArray(bg) ? bg[0] : bg) || '#8b949e';
      const val = Number((dataset.data || [])[pIndex] || 0);

      const item = document.createElement('div');
      item.className = 'custom-legend-item period-level-item';
      if (!isVisible) item.classList.add('is-hidden');
      item.tabIndex = 0;
      item.setAttribute('role', 'button');
      item.setAttribute('aria-pressed', isVisible ? 'true' : 'false');

      const onToggle = () => {
        chart.setDatasetVisibility(dIndex, !isVisible);
        chart.update();
        renderBarLegend(chart, containerId, periods);
      };

      item.addEventListener('click', onToggle);
      item.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          onToggle();
        }
      });

      // Color Square
      const colorBox = document.createElement('div');
      colorBox.className = 'legend-color-square';
      colorBox.style.backgroundColor = color;
      item.appendChild(colorBox);

      // Label & Data wrapper
      const infoWrap = document.createElement('div');
      infoWrap.className = 'legend-info-wrap';

      const labelEl = document.createElement('div');
      labelEl.className = 'legend-title';
      labelEl.textContent = label;

      const valueEl = document.createElement('div');
      valueEl.className = 'legend-stats';
      const pct = isVisible ? visiblePeriodTotals[pIndex] > 0 ? ((val / visiblePeriodTotals[pIndex]) * 100).toFixed(1) : '0.0' : '0.0';
      valueEl.innerHTML = `<span class="val-count">${val}</span> <span class="val-pct">(${pct}%)</span>`;

      infoWrap.appendChild(labelEl);
      infoWrap.appendChild(valueEl);
      item.appendChild(infoWrap);

      // Eye Icon
      const iconWrap = document.createElement('div');
      iconWrap.className = 'legend-eye-icon';
      iconWrap.innerHTML = isVisible ? svgEye : svgEyeOff;
      item.appendChild(iconWrap);

      pItems.appendChild(item);
    });

    pCard.appendChild(pItems);
    list.appendChild(pCard);
  });

  container.replaceChildren(list);
}

function renderLineLegend(chart: Chart<'line'>, container: HTMLDivElement, colors: string[]) {
  const datasets = chart.data.datasets;
  if (!datasets || datasets.length === 0) {
    container.innerHTML = '';
    return;
  }

  // Compute the average value per visible dataset so we can show a meaningful stat
  const datasetAverages = datasets.map((ds) => {
    const vals = (ds.data || []).map(v => Number(v || 0));
    if (vals.length === 0) return 0;
    return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length);
  });

  const list = document.createElement('div');
  list.className = 'custom-legend-list';

  datasets.forEach((dataset, dIndex) => {
    const meta = chart.getDatasetMeta(dIndex);
    const isVisible = meta.hidden === null || !meta.hidden;
    const label = String(dataset.label || `Dataset ${dIndex}`);
    const color = colors[dIndex] || '#8b949e';

    const item = document.createElement('div');
    item.className = 'custom-legend-item';
    if (!isVisible) item.classList.add('is-hidden');
    item.tabIndex = 0;
    item.setAttribute('role', 'button');
    item.setAttribute('aria-pressed', isVisible ? 'true' : 'false');

    const onToggle = () => {
      chart.setDatasetVisibility(dIndex, !isVisible);
      chart.update();
      renderLineLegend(chart, container, colors);
    };

    item.addEventListener('click', onToggle);
    item.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        onToggle();
      }
    });

    const colorBox = document.createElement('div');
    colorBox.className = 'legend-color-square';
    colorBox.style.backgroundColor = color;
    item.appendChild(colorBox);

    const infoWrap = document.createElement('div');
    infoWrap.className = 'legend-info-wrap';

    const labelEl = document.createElement('div');
    labelEl.className = 'legend-title';
    labelEl.textContent = label;

    const valueEl = document.createElement('div');
    valueEl.className = 'legend-stats';
    valueEl.innerHTML = `<span class="val-count">~${datasetAverages[dIndex]}</span> <span class="val-pct">prom.</span>`;

    infoWrap.appendChild(labelEl);
    infoWrap.appendChild(valueEl);
    item.appendChild(infoWrap);

    const iconWrap = document.createElement('div');
    iconWrap.className = 'legend-eye-icon';
    iconWrap.innerHTML = isVisible ? svgEye : svgEyeOff;
    item.appendChild(iconWrap);

    list.appendChild(item);
  });

  container.replaceChildren(list);
}