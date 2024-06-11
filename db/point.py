from sqlalchemy import func
from sqlalchemy.types import UserDefinedType, Float


class PostgresqlPoint(UserDefinedType):
    def get_col_spec(self):
        return "GEOMETRY"

    def bind_expression(self, bindvalue):
        return bindvalue

    def column_expression(self, col):
        return col

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            assert isinstance(value, tuple)
            lat, lng = value
            return "POINT(%s %s)" % (lng, lat)

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None
            # m = re.match(r'^POINT\((\S+) (\S+)\)$', value)
            # lng, lat = m.groups()
            if isinstance(value, str):
                lng, lat = value.lstrip("(").rstrip(")").split(",")
            else:
                lng, lat = value[6:-1].split()  # 'POINT(135.00 35.00)' => ('135.00', '35.00')
            return float(lat), float(lng)

        return process
