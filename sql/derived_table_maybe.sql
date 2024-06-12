select *
from (select * from boarding_passes where boarding_passes.flight_id = 4214) as boarding_passes
         right join (select * from seats where seats.aircraft_code = '763') as seats
                    on seats.seat_no = boarding_passes.seat_no
where boarding_passes.seat_no IS NULL;


select *
from (select * from boarding_passes where boarding_passes.flight_id = 4214) as boarding_passes
         right join seats
                    on seats.seat_no = boarding_passes.seat_no
where boarding_passes.seat_no IS NULL
  and seats.aircraft_code = '763';