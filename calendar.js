const daysOfWeek = [ 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];

const parseUTCDate = (dateString) => {
  const [year, month, day] = dateString.split('-').map(Number);
  return new Date(Date.UTC(year, month - 1, day)); // Month is zero-indexed
};

const fetchData = async(url) => {
  const response = await fetch(url)
  return response.text();
};

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


document.addEventListener('DOMContentLoaded', () => {
  const today = new Date();
  const todayStr = today.toISOString().split('T')[0];
  document.getElementById("currentDate").textContent = todayStr;
  const nextEventTable = document.getElementById("nextEvent");
  fetch('Eventos_de_la_Comunidad_Flesh_and_Blood_Q1_2025__D_as_en_Espa_ol_.csv')
    .then(response => response.text())
    .then(data => {
      const rows = data.split('\n').slice(1); // Skip header row
      const tableBody = document.querySelector('tbody');
      const events = {};
      const eventsByMonth = {};
      let next = false;
      rows.map(row => row.split(','))
          .filter(columns => columns.length === 6).sort((a, b) => {
            const dateA = parseUTCDate(a[0]);
            const dateB = parseUTCDate(b[0]);
            return dateA - dateB;
          }).forEach(columns => {
            events[columns[0]] = columns[5]; // Push date and emoji
            const eventDate  = parseUTCDate(columns[0]);
            const dateStr = eventDate.toISOString().split('T')[0];
            const eventMonth = new Intl.DateTimeFormat('es-ES', { month: 'long', timeZone : 'UTC' }).format(eventDate);
            const tr = document.createElement('tr');
            if(dateStr == todayStr) {
              tr.classList.add('today')
            }
            columns.forEach(col => {
              const td = document.createElement('td');
              td.textContent = col;
              tr.appendChild(td);
            });
            if(today < eventDate && !next){
              next = true;
              const cloned = tr.cloneNode(true)
              nextEventTable.appendChild(cloned);
              tr.classList.add('next');
            }

            if(!eventsByMonth[eventMonth]){
              eventsByMonth[eventMonth] = []
            }
            eventsByMonth[eventMonth].push(tr)
            
          });

      // Generate calendar
      const calendar = document.querySelector('.calendar');
      const firstDay = new Date(Date.UTC(2025,0,01));
      const lastDay = new Date(Date.UTC(2025,2,31));
      
      
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
        
        if(dateStr == todayStr) {
           div.classList.add('today');
        } 
        
        if (events[dateStr]) {
          if (currentDate < today.getUTCDate()) {
            div.classList.add('done')
          } else
          if (dateStr == todayStr) {
            div.classList.add('current')
          } else {
            div.classList.add('event');
          }
          div.textContent = div.textContent + events[dateStr]
        }

        month.grid.appendChild(div);
        currentDate.setUTCDate(currentDate.getUTCDate() + 1);
      }
    })
    .catch(error => console.error('Error loading CSV:', error));
});
