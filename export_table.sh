sqlacodegen_v2 postgresql:///demo > db/table.py
sed -i "s/from sqlalchemy.sql.sqltypes import NullType/from db.point import PostgresqlPoint/" db/table.py
sed -i "s/NullType/PostgresqlPoint/" db/table.py