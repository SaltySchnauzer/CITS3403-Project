window.addEventListener('DOMContentLoaded', () => {
  const sessionsData = {{ sessions_data|tojson }};
  const durations = sessionsData.map(s => s.duration_min);
  const dates = sessionsData.map(s => s.date);
  const weekdays = sessionsData.map(s => s.weekday);

  // Line chart: sessions over time
  new Chart(document.getElementById('sessions-over-time'), {
    type: 'line', data: { labels: dates, datasets: [{ label: 'Sessions', data: dates.map(_=>1) }] }
  });

  // Histogram of durations
  new Chart(document.getElementById('duration-histogram'), {
    type: 'bar', data: { labels: durations, datasets: [{ label: 'Duration (min)', data: durations }] }
  });

  // Pie: by weekday
  const byDay = weekdays.reduce((acc,d) => { acc[d] = (acc[d]||0)+1; return acc }, {});
  new Chart(document.getElementById('weekday-pie'), {
    type: 'pie', data: { labels: Object.keys(byDay), datasets:[{ data: Object.values(byDay) }] }
  });
});