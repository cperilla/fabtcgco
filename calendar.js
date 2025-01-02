document.addEventListener('DOMContentLoaded', () => {
  const parseUTCDate = (dateString) => {
    const [year, month, day] = dateString.split('-').map(Number);
    return new Date(Date.UTC(year, month - 1, day)); // Month is zero-indexed
  };

  fetch('Eventos_de_la_Comunidad_Flesh_and_Blood_Q1_2025__D_as_en_Espa_ol_.csv')
    .then(response => response.text())
    .then(data => {
      const rows = data.split('\n').slice(1); // Skip header row
      const tableBody = document.querySelector('tbody');
      const events = [];
      const eventsByMonth = {};
      rows.map(row => row.split(','))
          .filter(columns => columns.length === 6).sort((a, b) => {
            const dateA = parseUTCDate(a[0]);
            const dateB = parseUTCDate(b[0]);
            return dateA - dateB;
          }).forEach(columns => {
            events.push(columns[0]); // Push date
            const eventDate  = parseUTCDate(columns[0]);
            const eventMonth = new Intl.DateTimeFormat('es-ES', { month: 'long', timeZone : 'UTC' }).format(eventDate);
            const tr = document.createElement('tr');
            columns.forEach(col => {
              const td = document.createElement('td');
              td.textContent = col;
              tr.appendChild(td);
            });
            if(!eventsByMonth[eventMonth]){
              eventsByMonth[eventMonth] = []
            }
            eventsByMonth[eventMonth].push(tr)

          });

      // Generate calendar
      const calendar = document.querySelector('.calendar');
      const firstDay = new Date(Date.UTC(2025,0,01));
      const lastDay = new Date(Date.UTC(2025,2,31));
      const daysOfWeek = [ 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];

      function createMonth(calendar, currentDate) {
        const month = document.createElement('div');
        month.classList.add('month');
        const label =  document.createElement('div');
        label.textContent = new Intl.DateTimeFormat('es-ES', { month: 'long', timeZone : 'UTC' }).format(currentDate);
        month.appendChild(label);
        label.classList.add('label');
        const grid =  document.createElement('div');
        grid.classList.add('grid');
        month.appendChild(grid);
        // Add headers
        daysOfWeek.forEach(day => {
          const div = document.createElement('div');
          div.textContent = day;
          div.classList.add('header');
          grid.appendChild(div);
        });
        calendar.appendChild(month);

        let dayOfWeek = currentDate.getUTCDay() - 1;
        if( dayOfWeek < 0 ){
          dayOfWeek = 7
        }
        for (let i = 0; i < dayOfWeek; i++) {
          const div = document.createElement('div');
          div.classList.add('padding');
          grid.appendChild(div);
        }
        const table = document.createElement('table');
        const thead = document.createElement('thead');
        const tbody = document.createElement('tbody');

        // Add table headers
        thead.innerHTML = `
                    <tr>
                        <th>Fecha</th>
                        <th>Día</th>
                        <th>Evento</th>
                        <th>Hora</th>
                        <th>Ubicación</th>
                        <th>Reminder</th>
                    </tr>
                 `;


        table.appendChild(thead);
        table.appendChild(tbody);
        month.appendChild(table)
        return { 'grid': grid, 'table' : table };
      }
      // Fill calendar
      let currentDate = firstDay;
      let month = createMonth(calendar, currentDate);

      let lastMonth = new Intl.DateTimeFormat('es-ES', { month: 'long', timeZone : 'UTC' }).format(currentDate);
      eventsByMonth[lastMonth].forEach(tr => month.table.appendChild(tr));
      while (currentDate <= lastDay) {
        const div = document.createElement('div');
        const dateStr = currentDate.toISOString().split('T')[0];
        const curMonth = new Intl.DateTimeFormat('es-ES', { month: 'long', timeZone : 'UTC' }).format(currentDate);
        if (curMonth !== lastMonth){
          month = createMonth(calendar, currentDate);
          lastMonth = curMonth
          eventsByMonth[lastMonth].forEach(tr => month.table.appendChild(tr));
        }
        div.textContent = currentDate.getUTCDate();
        if (events.includes(dateStr)) {
          div.classList.add('event');
        }

        month.grid.appendChild(div);
        currentDate.setUTCDate(currentDate.getUTCDate() + 1);
      }
    })
    .catch(error => console.error('Error loading CSV:', error));
});
