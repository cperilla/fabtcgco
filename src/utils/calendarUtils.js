import { endOfMonth, startOfWeek, endOfWeek, format, isToday } from 'date-fns';
import { es } from 'date-fns/locale';

export const formatMonthName = (monthNumber, year) => {
  return format(new Date(year, monthNumber - 1, 1), 'MMMM', { locale: es });
};

export const getMonths = (eventsData) => {
  const months = new Set();
  eventsData.forEach((event) => {
    const month = new Date(event.Date).getMonth() + 1;
    months.add(month);
  });
  return Array.from(months).sort((a, b) => a - b);
};

export const getEventsOfMonth = (eventsData, month) => {
  const eventsByMonth = eventsData.filter((event) => {
    const eventMonth = new Date(event.Date).getMonth() + 1;
    return eventMonth === month;
  });

  eventsByMonth.sort((a, b) => new Date(a.Date) - new Date(b.Date));

  return eventsByMonth.reduce((acc, event) => {
    if (!acc[event.Date]) {
      acc[event.Date] = [];
    }
    acc[event.Date].push({
      icon: event.Emoji,
      type: event.EventType,
      title: event.Event,
      time: event.Time,
      location: {
        spot: event.Location,
        city: event.Ciudad,
      },
      date: event.Date,
    });
    return acc;
  }, {});
};

export const getCalendarDays = (year, month, eventsOfMonth) => {
  const firstDayOfMonth = new Date(year, month - 1, 1);
  const lastDayOfMonth = endOfMonth(firstDayOfMonth);

  const firstDayOfWeek = startOfWeek(firstDayOfMonth);
  const lastDayOfWeek = endOfWeek(lastDayOfMonth);

  const calendarDays = [];
  let currentDay = firstDayOfWeek;

  while (currentDay <= lastDayOfWeek) {
    const formattedDate = format(currentDay, 'yyyy-MM-dd');

    calendarDays.push({
      dayNumber: format(currentDay, 'd'),
      dateString: formattedDate,
      events: eventsOfMonth[formattedDate] || [],
    });

    currentDay.setDate(currentDay.getDate() + 1);
  }

  return calendarDays;
};

