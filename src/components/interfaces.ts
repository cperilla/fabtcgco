export interface Location {
    spot: string;
    city: string;
    address?: string;
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


function formatDateTimeICS(date: string, time: string): string {
  const match = time.trim().match(/^(\d{1,2})(?::(\d{2}))?\s*(AM|PM)$/i);
  if (!match) throw new Error(`Hora de evento inválida: ${time}`);
  const [, hourText, minuteText = '00', modifier] = match;
  const hour12 = Number(hourText);
  const minute = Number(minuteText);
  if (hour12 < 1 || hour12 > 12 || minute > 59) {
    throw new Error(`Hora de evento inválida: ${time}`);
  }
  const hour = hour12 % 12 + (modifier.toUpperCase() === 'PM' ? 12 : 0);
  return date.replace(/-/g, '') + 'T' + String(hour).padStart(2, '0') + minuteText + '00';
}

function getEventDescription(event: Event): string {
  return [
    event.description,
    event.registrationFee ? `Inscripción: ${event.registrationFee}` : null,
  ].filter(Boolean).join('\n') || `Evento de Flesh and Blood con FAB Colombia en ${event.location.spot}.`;
}

function getEventLocation(event: Event): string {
  return [event.location.spot, event.location.address, event.location.city].filter(Boolean).join(', ');
}

function escapeICS(value: string): string {
  return value.replace(/\\/g, '\\\\').replace(/\r?\n/g, '\\n').replace(/,/g, '\\,').replace(/;/g, '\\;');
}

// RFC 5545 limits content lines to 75 octets, including the continuation space.
function foldICSLine(line: string): string {
  const encoder = new TextEncoder();
  let output = '';
  let width = 0;
  for (const character of line) {
    const bytes = encoder.encode(character).length;
    if (width + bytes > 75) {
      output += '\r\n ';
      width = 1;
    }
    output += character;
    width += bytes;
  }
  return output;
}

export function generateICS(event: Event) {
  const start = formatDateTimeICS(event.date, event.time);
  const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z');
  const uid = encodeURIComponent(`${event.date}-${event.title}-${event.time}-${event.location.spot}`);
  // Only the start is confirmed; do not invent an event duration.
  return [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//FAB Colombia//Eventos de la comunidad//ES',
    'BEGIN:VTIMEZONE',
    'TZID:America/Bogota',
    'BEGIN:STANDARD',
    'DTSTART:19700101T000000',
    'TZOFFSETFROM:-0500',
    'TZOFFSETTO:-0500',
    'END:STANDARD',
    'END:VTIMEZONE',
    'BEGIN:VEVENT',
    `UID:${uid}@fabtcgcolombia.club`,
    `DTSTAMP:${stamp}`,
    `DTSTART;TZID=America/Bogota:${start}`,
    `SUMMARY:${escapeICS(event.title)}`,
    `LOCATION:${escapeICS(getEventLocation(event))}`,
    `DESCRIPTION:${escapeICS(getEventDescription(event))}`,
    'END:VEVENT',
    'END:VCALENDAR',
  ].map(foldICSLine).join('\r\n') + '\r\n';
}

export function getGoogleCalendarLink(event: Event) {
  const start = formatDateTimeICS(event.date, event.time);
  const params = new URLSearchParams({
    action: 'TEMPLATE',
    text: event.title,
    dates: `${start}/${start}`,
    ctz: 'America/Bogota',
    details: getEventDescription(event),
    location: getEventLocation(event),
    sf: 'true',
    output: 'xml',
  });
  return `https://calendar.google.com/calendar/render?${params}`;
}
