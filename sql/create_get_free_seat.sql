DROP FUNCTION IF EXISTS bookings.get_free_seat;

create function bookings.get_free_seat(in _ticket_no char(13),
                                       in _flight_id integer,
                                       out seat_no varchar(4))
    language sql
as
$$
select free_seats.seats_no
from (select *
      from ticket_flights
      where ticket_no = _ticket_no
        and flight_id = _flight_id) as ticket_flights
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
$$;



create function bookings.get_boarding_no(in _flight_id integer, out boarding_no varchar(4))
    language sql
as
$$
select max(boarding_passes.boarding_no) + 1
      from boarding_passes
      where flight_id = _flight_id
$$;

-- select get_free_seat('0005433924584', 4214);

-- select get_boarding_no(4214);