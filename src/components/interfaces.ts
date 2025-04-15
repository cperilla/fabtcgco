export interface Location {
    spot: string;
    city: string;
}
  
export interface Event {
    icon: string;
    type: string;
    title: string;
    time: string;
    location: Location;
    date: string;
}

export interface Day {
    dayNumber: string;
    dateString: string;
    events: Event[];
}


function estimateEndTime(dtStart: string): string {
  const year = parseInt(dtStart.slice(0, 4), 10);
  const month = parseInt(dtStart.slice(4, 6), 10) - 1; // JS months are 0-based
  const day = parseInt(dtStart.slice(6, 8), 10);
  const hour = parseInt(dtStart.slice(9, 11), 10);
  const minute = parseInt(dtStart.slice(11, 13), 10);
  const second = parseInt(dtStart.slice(13, 15), 10);

  const startDate = new Date(Date.UTC(year, month, day, hour, minute, second));
  const endDate = new Date(startDate.getTime() + 3 * 60 * 60 * 1000); // Add 3 hours

  const pad = (n: number) => String(n).padStart(2, '0');
  return (
    endDate.getUTCFullYear().toString() +
    pad(endDate.getUTCMonth() + 1) +
    pad(endDate.getUTCDate()) + 'T' +
    pad(endDate.getUTCHours()) +
    pad(endDate.getUTCMinutes()) +
    pad(endDate.getUTCSeconds()) + 'Z'
  );
}

function formatDateTimeICS(date, time) {
  // Example input: date = '2025-05-03', time = '3 PM'
  const [hourStr, modifier] = time.split(' ');
  const hour = parseInt(hourStr, 10) + (modifier === 'PM' && hourStr !== '12' ? 12 : 0);
  return date.replace(/-/g, '') + 'T' + String(hour).padStart(2, '0') + '0000Z'; // e.g. 20250503T150000Z
}

export function generateICS(event) {
  const dtStart = formatDateTimeICS(event.date, event.time);
  const dtEnd = estimateEndTime(dtStart); // add 2 hours for example

  return `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Chaos Store//Flesh and Blood Events//EN
BEGIN:VEVENT
UID:${event.date}-${event.title.replace(/\s/g, '')}@chaosstore
DTSTAMP:${dtStart}
DTSTART:${dtStart}
DTEND:${dtEnd}
SUMMARY:${event.title}
LOCATION:${event.location.spot}, ${event.location.city}
DESCRIPTION:Evento de Flesh and Blood en Chaos Store.
END:VEVENT
END:VCALENDAR`;
}
export function getGoogleCalendarLink(event) {
  const start = formatDateTimeICS(event.date, event.time);
  const end = estimateEndTime(start);

  return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(event.title)}&dates=${start}/${end}&details=${encodeURIComponent('Flesh and Blood - Chaos Store')}&location=${encodeURIComponent(event.location.spot + ', ' + event.location.city)}&sf=true&output=xml`;
}