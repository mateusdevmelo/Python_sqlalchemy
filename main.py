import sqlalchemy
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.orm import relationship
from sqlalchemy import Column, inspect, select, func
from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey

Base = declarative_base()


class Client(Base):
    __table_name__ = "client_account"
    #atributos
    id = Column(Integer, primary_key=True)
    name = Column(String)
    cpf = Column(String)
    address = Column(String)

    account = relationship(
        "Account", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, cpf={self.cpf}, address={self.address})"


class Account(Base):
    __table_name__ = "account"
    id = Column(Integer, primary_key=True)
    type = Column(String(30), nullable=False)
    agency = Column(String(30), nullable=False)
    num = Column(Integer, nullable=False)
    balance = Column(Integer, nullable=False)
    id_client = Column(Integer, ForeignKey("user_account.id"), nullable=False)

    client = relationship("Client", back_populates="account")

    def __repr__(self):
        return f"(id={self.id}, agency={self.agency})"


print(Client.__table_name__)
print(Account.__table_name__)

#conexão com o banco de dados
engine = create_engine("sqlite://")

#criando as classes como tabelas no banco de dados
Base.metadata.create_all(engine)

#investiga o esquema de banco de dados
inspetor_engine = inspect(engine)

print(inspetor_engine.has_table("account"))
print(inspetor_engine.get_table_names())
print(inspetor_engine.default_schema_name)

with Session(engine) as session:
    mateus = Client(
        name="mateus",
        cpf="000000000",
        address="Recife - Boa Viagem"
    )

    anna = Client(
        name="anna",
        cpf="1111111111",
        address="Rio De Janeiro - Flamengo"
    )


    #enviando para o DB (pesistência de dados)
    session.add_all([mateus, anna])

    session.commit()

stmt = select(Client).where(Client.name.in_(["anna", "mateus"]))
print("recuperando usuários a partir de matching")
for user in session.scalars(stmt):
    print(user)

stmt_address = select(Account).where(Account.user_id.in_([2]))
print("recuperando os endereços de email de anna")
for address in session.scalars(stmt_address):
    print(address)

stmt_order = select(Client).order_by(Client.fullname.desc())
print("\nrecuperando info de mandeira ordenada")
for result in session.scalars(stmt_order):
    print(result)

stmt_join = select(Client.fullname, Client.email_address).join_from(Account, Client)
for result in session.scalars(stmt_join):
    print(result)

connection = engine.connect()
results = connection.execute(stmt_join).fetchall()
print("Executando statement a partir da connection")
for result in results:
    print(result)

stmt_count = select(func.count("*")).select_from(Client)
print("\nTotal de instâncias em User")
for result in session.scalars(stmt_count):
    print(result)
