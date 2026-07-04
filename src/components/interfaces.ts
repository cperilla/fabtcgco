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
    tournamentUrl?: string;
    tournamentName?: string;
    registrationFee?: string;
    description?: string;
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

  const endDate = new Date(year, month, day, hour, minute, second);
  endDate.setHours(endDate.getHours() + 3);

  const pad = (n: number) => String(n).padStart(2, '0');
  return (
    endDate.getFullYear().toString() +
    pad(endDate.getMonth() + 1) +
    pad(endDate.getDate()) + 'T' +
    pad(endDate.getHours()) +
    pad(endDate.getMinutes()) +
    pad(endDate.getSeconds())
  );
}

function formatDateTimeICS(date: string, time: string): string {
  // Example input: date = '2025-05-03', time = '3 PM'
  const [hourStr, modifier] = time.split(' ');
  const hour = parseInt(hourStr, 10) + (modifier === 'PM' && hourStr !== '12' ? 12 : 0);
  return date.replace(/-/g, '') + 'T' + String(hour).padStart(2, '0') + '0000'; // e.g. 20250503T150000
}

function getEventDescription(event: Event): string {
  return [
    event.description,
    event.registrationFee ? `Inscripción: ${event.registrationFee}` : null,
  ].filter(Boolean).join('\\n') || 'Evento de Flesh and Blood en CHAOS Hobby Store.';
}

export function generateICS(event: Event) {
  const dtStart = formatDateTimeICS(event.date, event.time);
  const dtEnd = estimateEndTime(dtStart); // add 2 hours for example
  const description = getEventDescription(event);

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
DESCRIPTION:${description}
END:VEVENT
END:VCALENDAR`;
}
export function getGoogleCalendarLink(event: Event) {
  const start = formatDateTimeICS(event.date, event.time);
  const end = estimateEndTime(start);
  const details = getEventDescription(event);

  return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(event.title)}&dates=${start}/${end}&ctz=America%2FBogota&details=${encodeURIComponent(details)}&location=${encodeURIComponent(event.location.spot + ', ' + event.location.city)}&sf=true&output=xml`;
}
