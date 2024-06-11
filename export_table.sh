sqlacodegen_v2 postgresql:///demo > table.py
sed -i "s/from sqlalchemy.sql.sqltypes import NullType/from db.point import PostgresqlPoint/" table.py
sed -i "s/NullType/PostgresqlPoint/" table.py