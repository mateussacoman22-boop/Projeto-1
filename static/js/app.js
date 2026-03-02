const root = document.documentElement;
const toggle = document.getElementById('themeToggle');
if (toggle) {
  toggle.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  });
  root.setAttribute('data-theme', localStorage.getItem('theme') || 'light');
}

function createCharts() {
  if (!window.dashboardData || typeof Chart === 'undefined') return;

  const expenses = window.dashboardData.expensesByCategory;
  const trend = window.dashboardData.monthlyTrend;
  const evolution = window.dashboardData.balanceEvolution;

  new Chart(document.getElementById('pieChart'), {
    type: 'pie',
    data: { labels: Object.keys(expenses), datasets: [{ data: Object.values(expenses) }] },
    options: { plugins: { title: { display: true, text: 'Expenses by Category' } }, responsive: true }
  });

  const trendLabels = Object.keys(trend).sort();
  new Chart(document.getElementById('barChart'), {
    type: 'bar',
    data: {
      labels: trendLabels,
      datasets: [
        { label: 'Income', data: trendLabels.map((k) => trend[k].income), backgroundColor: '#17b26a' },
        { label: 'Expenses', data: trendLabels.map((k) => trend[k].expense), backgroundColor: '#f04438' }
      ]
    },
    options: { plugins: { title: { display: true, text: 'Monthly Income vs Expenses' } }, responsive: true }
  });

  new Chart(document.getElementById('lineChart'), {
    type: 'line',
    data: {
      labels: evolution.map((v) => v.date),
      datasets: [{ label: 'Balance Evolution', data: evolution.map((v) => v.balance), borderColor: '#155eef' }]
    },
    options: { plugins: { title: { display: true, text: 'Balance Evolution Over Time' } }, responsive: true }
  });

  const totalExpenses = Object.values(expenses).reduce((acc, val) => acc + val, 0);
  const percentageData = Object.values(expenses).map((value) => totalExpenses ? ((value / totalExpenses) * 100).toFixed(2) : 0);

  new Chart(document.getElementById('spendingShareChart'), {
    type: 'doughnut',
    data: { labels: Object.keys(expenses), datasets: [{ label: 'Spending %', data: percentageData }] },
    options: { plugins: { title: { display: true, text: 'Spending Percentage by Category' } }, responsive: true }
  });
}

createCharts();
