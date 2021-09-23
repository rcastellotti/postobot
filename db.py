from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
Base = declarative_base()


class Lecture(Base):
    __tablename__ = 'Lectures'
    entry_id = Column(Integer, primary_key=True)
    sede = Column(String)
    aula = Column(String)
    data_lezione = Column(String)
    ora_inizio = Column(String)
    ora_fine = Column(String)
    qr = Column(String)
    nome = Column(String)
    ora_inizio_lezione = Column(String)
    ora_fine_lezione = Column(String)

    def __repr__(self):
        return f"{self.__class__}: {self.__dict__}"

    def __str__(self):
        return f"{self.data_lezione} {self.ora_inizio_lezione}-{self.ora_fine_lezione}\n{self.nome}\n{self.sede} {self.aula}"

