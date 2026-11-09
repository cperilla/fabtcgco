import activeCalendars from '../data/active-calendars.json' with { type: 'json' };

const calendarFiles = import.meta.glob('../data/Eventos_Comunidad_Q*.json', {
  eager: true,
  import: 'default',
});

export const loadEventsData = () => {
  return activeCalendars.flatMap((filename) => {
    const events = calendarFiles[`../data/${filename}`];
    if (!events) throw new Error(`Calendario activo no encontrado: ${filename}`);
    return events;
  }).sort((a, b) => a.Date.localeCompare(b.Date));
};
