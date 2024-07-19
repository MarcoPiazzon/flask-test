CREATE TABLE Utente(
    idUtente int PRIMARY KEY IDENTITY,
    nome varchar(255) NOT NULL,
    cognome varchar(255) NOT NULL,
    email varchar(255) NOT NULL,
    psw varchar(255)
);

CREATE TABLE Contatto(
    idContatto int PRIMARY KEY IDENTITY,
    idUtente int NOT NULL,
    nome varchar(255),
    secondoNome varchar(255),
    cognome varchar(255),
    viaUfficio1 varchar(255),
    viaUfficio2 varchar(255),
    viaUfficio3 varchar(255),
    citta varchar(255),
    provincia varchar(255),
    cap varchar(255),
    numUfficio varchar(255),
    numUfficio2 varchar(255),
    telefonoPrincipale varchar(255),
    faxAbitazione varchar(255),
    abitazione varchar(255),
    abitazione2 varchar(255),
    cellulare varchar(255),
    note varchar(255),
    numeroID varchar(255),
    paginaWeb varchar(255),
    email1 varchar(255),
    email2 varchar(255)
);

CREATE TABLE UtenteHaContatto(
    idUtente int NOT NULL,
    idContatto int NOT NULL,
    FOREIGN KEY (idUtente) REFERENCES Utente(idUtente),
    FOREIGN KEY (idContatto) REFERENCES Contatto(idContatto)
);

CREATE TABLE Portafoglio(
    idPortafoglio int PRIMARY KEY IDENTITY,
    idUtente int NOT NULL,
    dataInserimento int NOT NULL,
    FOREIGN KEY (idUtente) REFERENCES Utente(idUtente)
);

CREATE TABLE TipoCliente (
    idTipoCliente int PRIMARY KEY IDENTITY,
    nome varchar(255)
);

CREATE TABLE Presidio (
    idPresidio int NOT PRIMARY KEY IDENTITY,
    nome varchar(255)
);

CREATE TABLE Comune (
    idComune int NOT PRIMARY KEY IDENTITY,
    nome varchar(255),
    sigla varchar(255)
);


CREATE TABLE Cliente(
    idCliente int NOT PRIMARY KEY IDENTITY,
    idUtente int NOT NULL,
    idPortafoglio int NOT NULL,
    tipoCliente int,
    cf varchar(255),
    ragioneSociale varchar(255),
    presidio int,
    indirizzoPrincipale varchar(255),
    comunePrincipale int,
    capPrincipale varchar(255),
    provinciaDescPrincipale varchar(255),
    provinciaSiglaPrincipale varchar(255),
    sediTot int,
    nLineeTot int,
    fisso float,
    mobile float,
    totale float,
    fatturatoCerved varchar(255),
    clienteOffMobScadenza varchar(255),
    fatturatoTim float,
    dipendenti int,
    FOREIGN KEY (idUtente) REFERENCES Utente(idUtente),
    FOREIGN KEY (idPortafoglio) REFERENCES Portafoglio(idPortafoglio),
    FOREIGN KEY (tipoCliente) REFERENCES TipoCliente(idTipoCliente),
    FOREIGN KEY (presidio) REFERENCES Presidio(idPresidio),
    FOREIGN KEY (comunePrincipale) REFERENCES Comune(idComune)
);

CREATE TABLE Regione(
    idRegione int NOT PRIMARY KEY IDENTITY,
    nome varchar(255)
);

CREATE TABLE Categoria(
    idCategoria int PRIMARY KEY IDENTITY,
    nome varchar(255)
);

CREATE TABLE AndamentoTrattativa(
    idAndamento int PRIMARY KEY IDENTITY,
    nome varchar(255)
);

CREATE TABLE Trattativa(
    idTrattativa int PRIMARY KEY IDENTITY,
    idUtente int,
    idCliente int,
    codiceCtrDigitali varchar(255),
    codiceSalesHub varchar(255),
    areaManager varchar(255),
    zona int,
    tipo varchar(255),
    nomeOpportunita varchar(255),
    dataCreazioneOpportunita varchar(255),
    fix float,
    mobile float,
    categoriaOffertaIT int,
    it float,
    lineeFoniaFix float,
    aom float,
    mnp float,
    al float,
    dataChiusura date,
    fase int,
    noteSpecialista varchar(255),
    probabilita int,
    inPaf boolean,
    record int,
    fornitore varchar(255),
    FOREIGN KEY (idUtente) REFERENCES Utente(idUtente),
    FOREIGN KEY (idCliente) REFERENCES Cliente(idCliente),
    FOREIGN KEY (zona) REFERENCES Regione(idRegione),
    FOREIGN KEY (categoriaOffertaIT) REFERENCES Categoria(idCategoria),
    FOREIGN KEY (fase) REFERENCES AndamentoTrattativa(idAndamento)
);

CREATE TABLE Appuntamento(
    idAppuntamento int PRIMARY KEY IDENTITY,
    idUtenteCreazione int NOT NULL,
    idCalendario int NOT NULL,
    titolo varchar(255),
    varieDiscussioni varchar(255),
    preventivoDaFare varchar(255),
    dataApp date,
    FOREIGN KEY (idCalendario) REFERENCES Calendario(idCalendario),
    FOREIGN KEY (idUtenteCreazione) REFERENCES Utente(idUtente)
);

CREATE TABLE Partecipanti(
    idAppuntamento int NOT NULL,
    idUtente int NOT NULL,
    FOREIGN KEY (idAppuntamento) REFERENCES Appuntamento(idAppuntamento),
    FOREIGN KEY (idUtente) REFERENCES Utente(idUtente)
);

CREATE TABLE TrattativaAppuntamento(
    idTrattativa int NOT NULL,
    idAppuntamento int NOT NULL,
    FOREIGN KEY (idTrattativa) REFERENCES Trattativa(idTrattativa),
    FOREIGN KEY (idAppuntamento) REFERENCES Appuntamento(idAppuntamento)
);

CREATE TABLE ClienteAppuntamento(
    idCliente int NOT NULL,
    idAppuntamento int NOT NULL,
    FOREIGN KEY (idCliente) REFERENCES Cliente(idCliente),
    FOREIGN KEY (idAppuntamento) REFERENCES Appuntamento(idAppuntamento)
);


DELIMITER $$

CREATE TRIGGER after_trattativa_insert
AFTER INSERT
ON trattativa FOR EACH ROW
BEGIN
    IF (NEW.codiceCtrDigitali IS NULL AND NEW.codiceSalesHub is null and NEW.areaManager is null and new.zona is null and new.tipo is null 
        and new.nomeOpportunita is null and new.dataCreazioneOpportunita is null and new.fix is null and new.mobile is null and new.categoriaOffertaIT is null 
        and new.it is null and new.lineeFoniaFix is null and new.aom is null and new.mnp is null and new.al is null and new.dataChiusura is null 
        and new.fase is null and new.noteSpecialista is null and new.probabilita is null and new.inPaf is null and new.record is null and new.fornitore is null) THEN
    	SIGNAL sqlstate '45001' set message_text = "No way ! You cannot do this !";
    END IF;
END$$

DELIMITER ;