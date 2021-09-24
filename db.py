from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, Integer, String, DateTime, Computed
from datetime import datetime
from sqlalchemy.util.langhelpers import hybridproperty
Base = declarative_base()


def data(context):
    a = context.get_current_parameters()['data_lezione']
    b = context.get_current_parameters()['ora_inizio_lezione']
    return datetime.strptime(f"{a} {b}", "%d/%m/%Y %H:%M")


class Lecture(Base):
    __tablename__ = 'Lectures'
    entry_id = Column(Integer, primary_key=True)
    sede = Column(String)
    aula = Column(String)
    data_lezione = Column("data_lezione", String)
    ora_inizio = Column(String)
    ora_fine = Column(String)
    qr = Column(String)
    nome = Column(String)
    ora_inizio_lezione = Column("ora_inizio_lezione", String)
    ora_fine_lezione = Column(String)
    lecture_timestamp = Column(DateTime(timezone=False), default=data)

    def __repr__(self):
        return f"{self.__class__}: {self.__dict__}"

    def __str__(self):
        return f"{self.entry_id}\n{self.data_lezione} {self.ora_inizio_lezione}-{self.ora_fine_lezione}\n{self.nome}\n{self.sede} {self.aula}"
