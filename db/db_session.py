import sqlalchemy as sa
import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm as orm
from sqlalchemy import Engine
from sqlalchemy.orm import Session

SqlAlchemyBase = dec.declarative_base()
__factory = None
__engine: Engine | None = None


def global_init():
    global __factory
    if __factory:
        return
    global __engine
    conn_str = f'postgresql:///demo'
    print(f"Подключение к базе данных по адресу {conn_str}")
    __engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=__engine)
    SqlAlchemyBase.metadata.create_all(__engine)


def create_session() -> Session:
    global __factory
    return __factory()


def get_engine() -> Engine:
    global __engine
    return __engine
