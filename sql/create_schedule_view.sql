-- noinspection SqlShouldBeInGroupByForFile
-- noinspection SqlResolveForFile @ routine/"any_value"

DROP VIEW IF EXISTS bookings.schedule_routes;

CREATE VIEW bookings.schedule_routes AS
SELECT f1.flight_no,
       f1.departure_airport,
       f1.arrival_airport,
       f1.aircraft_code,
       avg(duration)                           as duration,
       to_char(any_value(scheduled_departure), 'hh24:mm:ss TZH:TZM') as scheduled_departure,
       to_char(any_value(scheduled_arrival), 'hh24:mm:ss TZH:TZM')    as scheduled_arrival,
       array_agg(DISTINCT f1.days_of_week)     as days_of_week
FROM (SELECT flights.flight_no,
             flights.departure_airport,
             flights.arrival_airport,
             flights.aircraft_code,
             flights.scheduled_arrival - flights.scheduled_departure   AS duration,
             flights.scheduled_departure,
             flights.scheduled_arrival,
             to_char(flights.scheduled_departure, 'ID'::text)::integer AS days_of_week
      FROM flights) f1
GROUP BY flight_no, departure_airport, arrival_airport, aircraft_code;