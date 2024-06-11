select flights.departure_airport,
       flights.arrival_airport,
       aircraft_code,
       fare_conditions,
       min(ticket_flights.amount) as amount
from ticket_flights
         join boarding_passes on (ticket_flights.ticket_no, ticket_flights.flight_id) =
                                 (boarding_passes.ticket_no, boarding_passes.flight_id)
         join flights on flights.flight_id = boarding_passes.flight_id
group by (flights.departure_airport, flights.arrival_airport, aircraft_code, fare_conditions)