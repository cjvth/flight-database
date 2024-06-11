from typing import List

from sqlalchemy import ARRAY, CHAR, CheckConstraint, Column, DateTime, ForeignKeyConstraint, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import INTERVAL, JSONB
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped
from geoalchemy2 import Geometry 

from db.point import PostgresqlPoint

class RawGeometry(Geometry): 
    # This class is used to remove the ST_AsEWKB() function from select queries 
    def column_expression(self, col): 
        return col 
        

Base = declarative_base()
metadata = Base.metadata


t_aircrafts = Table(
    'aircrafts', metadata,
    Column('aircraft_code', CHAR(3), comment='Aircraft code, IATA'),
    Column('model', Text, comment='Aircraft model'),
    Column('range', Integer, comment='Maximal flying distance, km'),
    comment='Aircrafts'
)


class AircraftsData(Base):
    __tablename__ = 'aircrafts_data'
    __table_args__ = (
        CheckConstraint('range > 0', name='aircrafts_range_check'),
        PrimaryKeyConstraint('aircraft_code', name='aircrafts_pkey'),
        {'comment': 'Aircrafts (internal data)'}
    )

    aircraft_code = mapped_column(CHAR(3), comment='Aircraft code, IATA')
    model = mapped_column(JSONB, nullable=False, comment='Aircraft model')
    range = mapped_column(Integer, nullable=False, comment='Maximal flying distance, km')

    flights: Mapped[List['Flights']] = relationship('Flights', uselist=True, back_populates='aircrafts_data')
    seats: Mapped[List['Seats']] = relationship('Seats', uselist=True, back_populates='aircrafts_data')


t_airports = Table(
    'airports', metadata,
    Column('airport_code', CHAR(3), comment='Airport code'),
    Column('airport_name', Text, comment='Airport name'),
    Column('city', Text, comment='City'),
    Column('coordinates', PostgresqlPoint, comment='Airport coordinates (longitude and latitude)'),
    Column('timezone', Text, comment='Airport time zone'),
    comment='Airports'
)


class AirportsData(Base):
    __tablename__ = 'airports_data'
    __table_args__ = (
        PrimaryKeyConstraint('airport_code', name='airports_data_pkey'),
        {'comment': 'Airports (internal data)'}
    )

    airport_code = mapped_column(CHAR(3), comment='Airport code')
    airport_name = mapped_column(JSONB, nullable=False, comment='Airport name')
    city = mapped_column(JSONB, nullable=False, comment='City')
    coordinates = mapped_column(PostgresqlPoint, nullable=False, comment='Airport coordinates (longitude and latitude)')
    timezone = mapped_column(Text, nullable=False, comment='Airport time zone')

    flights: Mapped[List['Flights']] = relationship('Flights', uselist=True, foreign_keys='[Flights.arrival_airport]', back_populates='airports_data')
    flights_: Mapped[List['Flights']] = relationship('Flights', uselist=True, foreign_keys='[Flights.departure_airport]', back_populates='airports_data_')


class Bookings(Base):
    __tablename__ = 'bookings'
    __table_args__ = (
        PrimaryKeyConstraint('book_ref', name='bookings_pkey'),
        {'comment': 'Bookings'}
    )

    book_ref = mapped_column(CHAR(6), comment='Booking number')
    book_date = mapped_column(DateTime(True), nullable=False, comment='Booking date')
    total_amount = mapped_column(Numeric(10, 2), nullable=False, comment='Total booking cost')

    tickets: Mapped[List['Tickets']] = relationship('Tickets', uselist=True, back_populates='bookings')


t_flights_v = Table(
    'flights_v', metadata,
    Column('flight_id', Integer, comment='Flight ID'),
    Column('flight_no', CHAR(6), comment='Flight number'),
    Column('scheduled_departure', DateTime(True), comment='Scheduled departure time'),
    Column('scheduled_departure_local', DateTime, comment='Scheduled departure time, local time at the point of departure'),
    Column('scheduled_arrival', DateTime(True), comment='Scheduled arrival time'),
    Column('scheduled_arrival_local', DateTime, comment='Scheduled arrival time, local time at the point of destination'),
    Column('scheduled_duration', INTERVAL, comment='Scheduled flight duration'),
    Column('departure_airport', CHAR(3), comment='Deprature airport code'),
    Column('departure_airport_name', Text, comment='Departure airport name'),
    Column('departure_city', Text, comment='City of departure'),
    Column('arrival_airport', CHAR(3), comment='Arrival airport code'),
    Column('arrival_airport_name', Text, comment='Arrival airport name'),
    Column('arrival_city', Text, comment='City of arrival'),
    Column('status', String(20), comment='Flight status'),
    Column('aircraft_code', CHAR(3), comment='Aircraft code, IATA'),
    Column('actual_departure', DateTime(True), comment='Actual departure time'),
    Column('actual_departure_local', DateTime, comment='Actual departure time, local time at the point of departure'),
    Column('actual_arrival', DateTime(True), comment='Actual arrival time'),
    Column('actual_arrival_local', DateTime, comment='Actual arrival time, local time at the point of destination'),
    Column('actual_duration', INTERVAL, comment='Actual flight duration'),
    comment='Flights (extended)'
)


t_routes = Table(
    'routes', metadata,
    Column('flight_no', CHAR(6), comment='Flight number'),
    Column('departure_airport', CHAR(3), comment='Code of airport of departure'),
    Column('departure_airport_name', Text, comment='Name of airport of departure'),
    Column('departure_city', Text, comment='City of departure'),
    Column('arrival_airport', CHAR(3), comment='Code of airport of arrival'),
    Column('arrival_airport_name', Text, comment='Name of airport of arrival'),
    Column('arrival_city', Text, comment='City of arrival'),
    Column('aircraft_code', CHAR(3), comment='Aircraft code, IATA'),
    Column('duration', INTERVAL, comment='Scheduled duration of flight'),
    Column('days_of_week', ARRAY(Integer()), comment='Days of week on which flights are scheduled'),
    comment='Routes'
)


class Flights(Base):
    __tablename__ = 'flights'
    __table_args__ = (
        CheckConstraint('actual_arrival IS NULL OR actual_departure IS NOT NULL AND actual_arrival IS NOT NULL AND actual_arrival > actual_departure', name='flights_check1'),
        CheckConstraint('scheduled_arrival > scheduled_departure', name='flights_check'),
        CheckConstraint("status::text = ANY (ARRAY['On Time'::character varying::text, 'Delayed'::character varying::text, 'Departed'::character varying::text, 'Arrived'::character varying::text, 'Scheduled'::character varying::text, 'Cancelled'::character varying::text])", name='flights_status_check'),
        ForeignKeyConstraint(['aircraft_code'], ['aircrafts_data.aircraft_code'], name='flights_aircraft_code_fkey'),
        ForeignKeyConstraint(['arrival_airport'], ['airports_data.airport_code'], name='flights_arrival_airport_fkey'),
        ForeignKeyConstraint(['departure_airport'], ['airports_data.airport_code'], name='flights_departure_airport_fkey'),
        PrimaryKeyConstraint('flight_id', name='flights_pkey'),
        UniqueConstraint('flight_no', 'scheduled_departure', name='flights_flight_no_scheduled_departure_key'),
        {'comment': 'Flights'}
    )

    flight_id = mapped_column(Integer, comment='Flight ID')
    flight_no = mapped_column(CHAR(6), nullable=False, comment='Flight number')
    scheduled_departure = mapped_column(DateTime(True), nullable=False, comment='Scheduled departure time')
    scheduled_arrival = mapped_column(DateTime(True), nullable=False, comment='Scheduled arrival time')
    departure_airport = mapped_column(CHAR(3), nullable=False, comment='Airport of departure')
    arrival_airport = mapped_column(CHAR(3), nullable=False, comment='Airport of arrival')
    status = mapped_column(String(20), nullable=False, comment='Flight status')
    aircraft_code = mapped_column(CHAR(3), nullable=False, comment='Aircraft code, IATA')
    actual_departure = mapped_column(DateTime(True), comment='Actual departure time')
    actual_arrival = mapped_column(DateTime(True), comment='Actual arrival time')

    aircrafts_data: Mapped['AircraftsData'] = relationship('AircraftsData', back_populates='flights')
    airports_data: Mapped['AirportsData'] = relationship('AirportsData', foreign_keys=[arrival_airport], back_populates='flights')
    airports_data_: Mapped['AirportsData'] = relationship('AirportsData', foreign_keys=[departure_airport], back_populates='flights_')
    ticket_flights: Mapped[List['TicketFlights']] = relationship('TicketFlights', uselist=True, back_populates='flight')


class Seats(Base):
    __tablename__ = 'seats'
    __table_args__ = (
        CheckConstraint("fare_conditions::text = ANY (ARRAY['Economy'::character varying::text, 'Comfort'::character varying::text, 'Business'::character varying::text])", name='seats_fare_conditions_check'),
        ForeignKeyConstraint(['aircraft_code'], ['aircrafts_data.aircraft_code'], ondelete='CASCADE', name='seats_aircraft_code_fkey'),
        PrimaryKeyConstraint('aircraft_code', 'seat_no', name='seats_pkey'),
        {'comment': 'Seats'}
    )

    aircraft_code = mapped_column(CHAR(3), nullable=False, comment='Aircraft code, IATA')
    seat_no = mapped_column(String(4), nullable=False, comment='Seat number')
    fare_conditions = mapped_column(String(10), nullable=False, comment='Travel class')

    aircrafts_data: Mapped['AircraftsData'] = relationship('AircraftsData', back_populates='seats')


class Tickets(Base):
    __tablename__ = 'tickets'
    __table_args__ = (
        ForeignKeyConstraint(['book_ref'], ['bookings.book_ref'], name='tickets_book_ref_fkey'),
        PrimaryKeyConstraint('ticket_no', name='tickets_pkey'),
        {'comment': 'Tickets'}
    )

    ticket_no = mapped_column(CHAR(13), comment='Ticket number')
    book_ref = mapped_column(CHAR(6), nullable=False, comment='Booking number')
    passenger_id = mapped_column(String(20), nullable=False, comment='Passenger ID')
    passenger_name = mapped_column(Text, nullable=False, comment='Passenger name')
    contact_data = mapped_column(JSONB, comment='Passenger contact information')

    bookings: Mapped['Bookings'] = relationship('Bookings', back_populates='tickets')
    ticket_flights: Mapped[List['TicketFlights']] = relationship('TicketFlights', uselist=True, back_populates='tickets')


class TicketFlights(Base):
    __tablename__ = 'ticket_flights'
    __table_args__ = (
        CheckConstraint('amount >= 0::numeric', name='ticket_flights_amount_check'),
        CheckConstraint("fare_conditions::text = ANY (ARRAY['Economy'::character varying::text, 'Comfort'::character varying::text, 'Business'::character varying::text])", name='ticket_flights_fare_conditions_check'),
        ForeignKeyConstraint(['flight_id'], ['flights.flight_id'], name='ticket_flights_flight_id_fkey'),
        ForeignKeyConstraint(['ticket_no'], ['tickets.ticket_no'], name='ticket_flights_ticket_no_fkey'),
        PrimaryKeyConstraint('ticket_no', 'flight_id', name='ticket_flights_pkey'),
        {'comment': 'Flight segment'}
    )

    ticket_no = mapped_column(CHAR(13), nullable=False, comment='Ticket number')
    flight_id = mapped_column(Integer, nullable=False, comment='Flight ID')
    fare_conditions = mapped_column(String(10), nullable=False, comment='Travel class')
    amount = mapped_column(Numeric(10, 2), nullable=False, comment='Travel cost')

    flight: Mapped['Flights'] = relationship('Flights', back_populates='ticket_flights')
    tickets: Mapped['Tickets'] = relationship('Tickets', back_populates='ticket_flights')


class BoardingPasses(TicketFlights):
    __tablename__ = 'boarding_passes'
    __table_args__ = (
        ForeignKeyConstraint(['ticket_no', 'flight_id'], ['ticket_flights.ticket_no', 'ticket_flights.flight_id'], name='boarding_passes_ticket_no_fkey'),
        PrimaryKeyConstraint('ticket_no', 'flight_id', name='boarding_passes_pkey'),
        UniqueConstraint('flight_id', 'boarding_no', name='boarding_passes_flight_id_boarding_no_key'),
        UniqueConstraint('flight_id', 'seat_no', name='boarding_passes_flight_id_seat_no_key'),
        {'comment': 'Boarding passes'}
    )

    ticket_no = mapped_column(CHAR(13), nullable=False, comment='Ticket number')
    flight_id = mapped_column(Integer, nullable=False, comment='Flight ID')
    boarding_no = mapped_column(Integer, nullable=False, comment='Boarding pass number')
    seat_no = mapped_column(String(4), nullable=False, comment='Seat number')
