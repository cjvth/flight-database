select free_seats.seats_no
from (select *
      from ticket_flights
      where ticket_no = '0005433924584'
        and flight_id = '4214') as ticket_flights
         join flights on ticket_flights.flight_id = flights.flight_id
         cross join lateral
    (select seats.seat_no as seats_no, seats.fare_conditions as fare_conditions
     from (select * from boarding_passes where boarding_passes.flight_id = flights.flight_id) as boarding_passes
              right join (select *
                          from seats
                          where seats.aircraft_code = flights.aircraft_code
                            and seats.fare_conditions = ticket_flights.fare_conditions) as seats
                         on seats.seat_no = boarding_passes.seat_no
     where boarding_passes.seat_no IS NULL) as free_seats
limit 1
