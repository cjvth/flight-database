select *
from (select *
      from ticket_flights
               join flights on ticket_flights.flight_id = flights.flight_id
      where status in ('On Time', 'Delayed')) as ticket_flights
         left join boarding_passes
                   on ticket_flights.ticket_no = boarding_passes.ticket_no
         join tickets on ticket_flights.ticket_no = tickets.ticket_no
where boarding_passes.ticket_no is null

