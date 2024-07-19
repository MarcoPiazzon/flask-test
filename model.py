import string
from sqlalchemy import *
from flask_login import *
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DB_LINK'))
metadata=MetaData()
conn=engine.connect()

andamentotrattativa = Table('andamentotrattativa',metadata, autoload_with=engine) 
appuntamento = Table('appuntamento',metadata, autoload_with=engine)
categoria = Table('categoria',metadata, autoload_with=engine)
cliente = Table('cliente',metadata, autoload_with=engine)
clienteappuntamento = Table('clienteappuntamento',metadata, autoload_with=engine)
#comune = Table('comune',metadata, autoload_with=engine)
contatto = Table('contatto',metadata, autoload_with=engine)
it_table = Table('it',metadata, autoload_with=engine)

partecipanti = Table('partecipanti',metadata, autoload_with=engine)
portafoglio = Table('portafoglio',metadata, autoload_with=engine)
#presidio = Table('presidio',metadata, autoload_with=engine)
#regione = Table('regione',metadata, autoload_with=engine)
tipocliente = Table('tipocliente',metadata, autoload_with=engine)
trattativa = Table('trattativa',metadata, autoload_with=engine)
trattativaappuntamento = Table('trattativaappuntamento',metadata, autoload_with=engine)
utente = Table('utente',metadata, autoload_with=engine)
utentehacontatto = Table('utentehacontatto',metadata, autoload_with=engine)

class User(UserMixin):
    
    def __init__(self,id,email) -> None:
        self.id=id
        self.email=email
        self.idPort = 0
        res =conn.execute(select(utente.c.nome, utente.c.cognome).where(utente.c.email==email)).fetchone()._asdict()
        print("sono qua")
        res2 = conn.execute(select(portafoglio.c.idportafoglio).where(portafoglio.c.idutente == id).order_by(portafoglio.c.idportafoglio.desc())).fetchone()[0]
        print(res2)
        if not (res2 is None):
            res2 = res2
        self.idPort = res2
        print(self.idPort)
        print(res)
        self.nome = res['nome']
        self.cognome = res['cognome']
    @property
    def getnames(self) -> string:
        return self.nome +" "+self.cognome
