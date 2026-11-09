import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { generateICS, getGoogleCalendarLink } from '../src/components/interfaces.ts';
import { getEventsOfMonth } from '../src/utils/calendarUtils.js';

const readData = (filename) => JSON.parse(readFileSync(new URL(`../src/data/${filename}`, import.meta.url), 'utf8'));
const events = readData('active-calendars.json').flatMap(readData);
const shinsei = readData('shinsei.json');
const toEvent = (raw) => ({
  date: raw.Date, time: raw.Time, title: raw.Event, type: raw.EventType, icon: raw.Emoji,
  description: raw.Description,
  location: { spot: raw.Location, city: raw.Ciudad, address: raw.LocationAddress },
});

test('el trimestre cruzado conserva todas las recurrencias y las excepciones confirmadas', () => {
  const keys = events.map(e => [e.Date, e.Location, e.Event, e.Time].join('|'));
  assert.equal(new Set(keys).size, events.length, 'sin duplicados');
  assert.equal(events.length, 51);
  assert.equal(events.filter(e => e.Location === 'Shinsei Store').length, 12);
  assert.equal(events.filter(e => e.Location === 'Chaos Store' && e.EventType === 'CC').length, 13);
  assert.equal(events.filter(e => e.EventType === 'FreePlay').length, 13);
  assert.equal(events.filter(e => e.Location === 'Palmira').length, 13);
  for (let date = new Date('2026-11-12T12:00:00Z'); date <= new Date('2027-02-12T12:00:00Z'); date.setUTCDate(date.getUTCDate() + 1)) {
    const iso = date.toISOString().slice(0, 10);
    const daily = events.filter(e => e.Date === iso);
    const excluded = shinsei.excludedDates.includes(iso);
    const expectedCount = excluded ? 0 : ({ 2: 1, 4: 1, 6: 2 }[date.getUTCDay()] ?? 0);
    assert.equal(daily.length, expectedCount, iso);
  }
  for (const e of events) {
    assert.ok(e.Date >= shinsei.startDate && e.Date <= shinsei.endDate);
    assert.notEqual(e.EventType, 'LL');
    assert.equal(e.RegistrationFee, undefined);
    if (e.Location === 'Shinsei Store') {
      assert.equal(e.Day, 'Jueves');
      assert.equal(e.Time, '5 PM');
      assert.equal(e.Event, 'Silver Age');
      assert.equal(e.LocationAddress, shinsei.address);
      assert.match(e.Description, /anticipación.*Mesa Inicial/);
      assert.ok(e.Description.includes(`Premios del set ${shinsei.prizeSet}.`));
    }
  }
});

test('la fecha del primer día de mes no retrocede por la zona horaria de Colombia', () => {
  const monthly = getEventsOfMonth(events, 12);
  assert.ok(monthly['2026-12-01']);
  assert.equal(monthly['2026-12-01'][0].location.spot, 'Chaos Store');
  assert.equal(monthly['2026-12-03'][0].location.address, shinsei.address);
});

test('iCal exporta Shinsei con dirección, zona horaria y texto escapado, sin duración inventada', () => {
  const e = toEvent(events.find(e => e.Location === shinsei.name));
  e.description = 'Mesa Inicial; preparación, mazo\nAvisa antes.';
  const raw = generateICS(e);
  for (const line of raw.trimEnd().split('\r\n')) assert.ok(Buffer.byteLength(line) <= 75);
  const ics = raw.replace(/\r\n /g, '');
  assert.match(ics, /DTSTART;TZID=America\/Bogota:20261112T170000/);
  assert.match(ics, /LOCATION:Shinsei Store\\, Cra\. 52B #18-40\\, Cali/);
  assert.ok(ics.includes('DESCRIPTION:Mesa Inicial\\; preparación\\, mazo\\nAvisa antes.'));
  assert.match(ics, /DTSTAMP:\d{8}T\d{6}Z/);
  assert.doesNotMatch(ics, /CHAOS|chaosstore|DTEND/);
  const other = generateICS({ ...e, location: { spot: 'Palmira', city: 'Palmira' } }).replace(/\r\n /g, '');
  assert.notEqual(ics.match(/UID:(.*)/)[1], other.match(/UID:(.*)/)[1]);
});

test('Google Calendar conserva sede, dirección y las 5 p. m. de Colombia', () => {
  const e = toEvent(events.find(e => e.Date === '2027-01-07' && e.Location === shinsei.name));
  const { searchParams: params } = new URL(getGoogleCalendarLink(e));
  assert.equal(params.get('dates'), '20270107T170000/20270107T170000');
  assert.equal(params.get('ctz'), 'America/Bogota');
  assert.equal(params.get('location'), 'Shinsei Store, Cra. 52B #18-40, Cali');
  assert.match(params.get('details'), /mesa-inicial/);
});
