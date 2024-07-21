from portafoglio import portafoglio_bp
from flask import Blueprint,render_template, url_for, redirect, request, Response
from flask_login import *
from home import *
from model import *
import openpyxl
from datetime import date
import io
import xlwt
import psycopg2
import psycopg2.extras

titolo = ""

#idPort: idPortafoglio
#id: idCliente
@portafoglio_bp.route('/<int:idPort>/<int:id>')
@login_required
def home(idPort, id):
    print("dentro home portafoglio")
    print(idPort)
    print(id)
    print(current_user.idport)
    print(type(idPort))
    print(type(id))
    print(id is None)
    if(idPort == 0):
        return render_template("home/home.html")
    current_user.idport = idPort
    clienti = None
    current_cliente = None
    trattative = None 
    getIt = None
    #namePortafoglio = conn.execute(select(portafoglio.c.dataInserimento).where(portafoglio.c.idPortafoglio == id)).fetchone()[0]
    t_len = 0
    getIt_len = 0
    #print()
    contatti = conn.execute(select(contatto).where(contatto.c.idutente == current_user.get_id()).order_by(contatto.c.nome)).fetchall()
    categorie = conn.execute(select(categoria)).fetchall()
    andamento = conn.execute(select(andamentotrattativa)).fetchall()
    if(idPort != 0):
        #fare la query in modo che prenda solo ragioneSociale e idCliente (ora lo fa)
        clienti = conn.execute(select(cliente.c.ragionesociale, cliente.c.idcliente).where(cliente.c.idportafoglio == idPort)).fetchall()
    if(id != 0):
        current_cliente = conn.execute(select(cliente).where(cliente.c.idcliente == id)).fetchone()
        trattative = conn.execute(
            select(trattativa, andamentotrattativa.c.nome, categoria.c.nome).
                join(andamentotrattativa).
                join(categoria) 
            .where(trattativa.c.idcliente == id)
            .order_by(trattativa.c.nomeopportunita)
        ).fetchall()
        print("tra")
        print(trattative)
        getIt = conn.execute(select(it_table, cliente.c.ragionesociale)
                             .join(cliente)
                             .where(it_table.c.idcliente == id)
                             ).fetchall()
        print(getIt)
        if not (getIt is None):
            getIt_len = len(getIt)
        #print(current_cliente)
        #print(trattative)
        
        

        if not (trattative is None):
            
        #select appuntamento.titolo, trattativa.nomeOpportunita from ((appuntamento join trattativaappuntamento on appuntamento.idAppuntamento = trattativaappuntamento.idAppuntamento)
        #join trattativa on trattativa.idTrattativa = trattativaappuntamento.idTrattativa)
            t_len = len(trattative)
            #print(type(trattative))
            for i in range(0, t_len):

                appuntamenti = conn.execute(select(appuntamento.c.titolo, appuntamento.c.dataapp).select_from(join(appuntamento,join(trattativaappuntamento,trattativa, trattativaappuntamento.c.idtrattativa == trattativa.c.idtrattativa), appuntamento.c.idappuntamento == trattativaappuntamento.c.idappuntamento)).where(trattativa.c.idtrattativa == trattative[i][0]).order_by(appuntamento.c.dataapp)).fetchall()
                
                #print(appuntamenti)
                #print(type(appuntamenti))
                trattative[i] = list(trattative[i])
                if (len(appuntamenti) > 0):
                    #print("Ho appuntamento")    
                    
                    trattative[i].append(appuntamenti)
                    #print(trattative[i][25])

                #print(len(trattative[i]))
    return render_template ("/portafoglio/portafoglio.html", clienti=clienti, current_cliente=current_cliente, trattative=trattative, t_len=t_len, idPort=idPort, categorie=categorie, andamento=andamento, contatti=contatti, name = "", getIt = getIt, getIt_len = getIt_len)


@portafoglio_bp.route('/portafoglio/<int:id>')
@login_required
def goToPortafoglio(id):
    # chiamata da fare successivamente quando verrà cambiata l'interfaccia grafica, permette di ricevere tutte le trattative dato un cliente
    return redirect(url_for('.home',idPort = id, id = 0))

@portafoglio_bp.route('/getCliente', methods=['POST'])
@login_required
def getCliente():
    #print(request.form)
    idPort = request.form['idPort']
    id=request.form['idSearch']
    current_user.idport = idPort
    return redirect(url_for('.home',idPort = idPort, id = id))

@portafoglio_bp.route('/remove/<int:id>', methods=['POST'])
@login_required
def removeTrattativa(id):
    print("test trattativa")
    print(id)
    getIdCliente = conn.execute(select(trattativa.c.idcliente).where(trattativa.c.idtrattativa == id)).fetchone()[0]
    try:
        print("")
        conn.execute(delete(trattativa).where(trattativa.c.idtrattativa == id))

        #appuntamenti = conn.execute(select(trattativaappuntamento).where(trattativa.c.idTrattativa == id)).fetchall()

        #if not (appuntamenti is None):
         #   for a in appuntamenti:
          #      conn.execute(delete(appuntamenti).where(appuntamenti.c.idAppuntamento == a.idAppuntamento))

        print("ho fatto")
    except Exception as error:
        print("rip")
        print(error.__cause__)
        conn.rollback()
    
    return redirect(url_for('.home',idPort = current_user.idport, id = getIdCliente))

@portafoglio_bp.route('/removeCliente/<int:id>', methods=['POST'])
@login_required
def removeCliente(id):
    print("REMOVE CLIENTE")
    conn.execute(delete(appuntamento).\
                                where(appuntamento.c.idappuntamento == trattativaappuntamento.c.idappuntamento).\
                                where(trattativaappuntamento.c.idtrattativa == trattativa.c.idtrattativa).\
                                where(trattativa.c.idcliente == cliente.c.idcliente).\
                                where(cliente.c.idcliente == id)                                                    
    )

    #Cancello tabella trattativaappuntamento


    conn.execute(delete(trattativaappuntamento).\
            where(trattativa.c.idcliente == cliente.c.idcliente).\
            where(trattativaappuntamento.c.idtrattativa == trattativa.c.idtrattativa).\
            where(trattativa.c.idcliente == cliente.c.idcliente).\
            where(cliente.c.idcliente == id)
    )
    

    #Cancello trattattive
    # delete trattativa from trattativa join cliente on trattativa.idCliente = cliente.idCliente where cliente.idPortafoglio = 6;
    conn.execute(delete(trattativa).\
                where(trattativa.c.idcliente == cliente.c.idcliente).\
                where(cliente.c.idcliente == id)
    )
    
    #Cancello clienti
    conn.execute(delete(cliente).where(cliente.c.idcliente == id))
    print("HO FATTO TUTTO")
    return redirect(url_for('.home', idPort = current_user.idport, id = 0))

@portafoglio_bp.route('/add', methods=['POST'])
@login_required
def addCliente():
    newId = 0
    try:
        print("addCliente")
        idPort = request.form['idPort']
        ragioneSociale = request.form['ragioneSociale']
        cf = request.form['cf']
        presidio = request.form['presidio']
        indirizzoPrincipale = request.form['indirizzo']
        capPrincipale = request.form['capPrincipale']
        comunePrincipale = request.form['comunePrincipale']
        sediTot = request.form['sediTot']
        dipendenti = request.form['dipendenti']
        nLineeTot = request.form['nLineeTot']
        fisso = request.form['fisso']
        mobile = request.form['mobile']
        totale = request.form['totale']
        fatturatoCerved = request.form['fatturatoCerved']
        fatturatoTim = request.form['fatturatoTim']

        ris = conn.execute(
            insert(cliente).values(
                idUtente = current_user.get_id(),
                idPortafoglio = idPort,
                ragioneSociale = ragioneSociale,
                cf = cf,
                presidio = presidio,
                indirizzoPrincipale = indirizzoPrincipale,
                capPrincipale = capPrincipale,
                comunePrincipale = comunePrincipale,
                sediTot = sediTot,
                dipendenti = dipendenti,
                nLineeTot = nLineeTot,
                fisso = fisso,
                mobile = mobile,
                totale = totale,
                fatturatoCerved = fatturatoCerved,
                fatturatoTim = fatturatoTim,
            )
        )
        newId = ris.inserted_primary_key[0]
        conn.commit()
        print("tutto bvene")
    except Exception as error:
        print("rip")
        print(error.__cause__)
        conn.rollback()
    

    return redirect(url_for('.home',idPort = idPort, id = newId))

def checkDate(val):
    if(isinstance(val, str)):
        if val == '':
            return None
        else: 
            return val 

def checkNull(val):
    print(type(val))
    if val == '':
        return 0
    else: 
        return val

@portafoglio_bp.route('/modifyTrattativa/<int:id>', methods=['POST'])
@login_required
def modifyTrattativa(id):
    print("modifiy Trattativa prova")
    print(id)
    print(request.form)
    
    idPort = 0
    try:
        idPort = request.form['idPortModify']
        idCliente = request.form['idClienteModify']
        codiceCtrDigitali = request.form['codiceCtrDigitaliModify']
        codiceSalesHub = request.form['codiceSalesHubModify']
        zona = request.form['zonaModify'] 
        tipo = request.form['tipoModify']
        nomeOpportunita = request.form['nomeOpportunitaModify']
        dataCreazioneOpportunita = request.form['dataCreazioneOpportunitaModify']
        
        fix = checkNull(request.form['fixModify'])
        mobile = checkNull(request.form['mobileModify'])
        categoriaOffertaIT = request.form['categoriaOffertaITModify'] 
        it = checkNull(request.form['itModify'])
        
        lineeFoniaFix = checkNull(request.form['lineeFoniaFixModify'])
        aom = checkNull(request.form['aomModify'])
        mnp = checkNull(request.form['mnpModify'])
        
        al = checkNull(request.form['alModify'])
        dataChiusura = request.form['dataChiusuraModify']
        fase = request.form['faseModify']
        noteSpecialista = request.form['noteSpecialistaModify']
        probabilita = checkNull(request.form['probabilitaModify'])
        if not (probabilita is None):
            if("%" in probabilita):
                probabilita = probabilita[:-1]
        inPaf = request.form['inPafModify']
        fornitore = request.form['fornitoreModify']
        
        conn.execute(
            update(trattativa).where(trattativa.c.idtrattativa==id).values(
                idutente = current_user.get_id(),
                idcliente = idCliente,
                codicectrdigitali = codiceCtrDigitali,
                codicesaleshub = codiceSalesHub,
                zona = zona,
                tipo = tipo,
                nomeopportunita = nomeOpportunita,
                datacreazioneopportunita = dataCreazioneOpportunita,
                fix = fix,
                mobile = mobile,
                categoriaoffertait = categoriaOffertaIT,
                it = it,
                lineefoniafix = lineeFoniaFix,
                aom = aom,
                mnp = mnp,
                al = al,
                datachiusura = dataChiusura,
                fase = fase,
                notespecialista = noteSpecialista,
                probabilita = probabilita,
                inpaf = 1,
                fornitore = fornitore
            )
        )
        
        print("tutto bvene")
    except Exception as error:
        print("rip")
        print(error)
        print(error.__cause__)
        conn.rollback()


    return redirect(url_for('.home',idPort = idPort, id = idCliente))


@portafoglio_bp.route('/modifyCliente', methods=['POST'])
@login_required
def modifyCliente():
 
    try:
        print(request.form)
        idCliente = request.form['idCliente']
        ragioneSociale = request.form['ragioneSociale']
        cf = request.form['cf']
        presidio = request.form['presidio']
        indirizzoPrincipale = request.form['indirizzo']
        capPrincipale = request.form['capPrincipale']
        comunePrincipale = request.form['comunePrincipale']
        sediTot = request.form['sediTot']
        dipendenti = request.form['dipendenti']
        nLineeTot = request.form['nLineeTot']
        fisso = request.form['fisso']
        mobile = request.form['mobile']
        totale = request.form['totale']
        fatturatoCerved = request.form['fatturatoCerved']
        fatturatoTim = request.form['fatturatoTim']
        print(idCliente)
        print(sediTot)
        print(type(sediTot))
        

        conn.execute(
            update(cliente).where(cliente.c.idcliente==idCliente).values(
                idcliente = idCliente,
                ragionesociale = ragioneSociale,
                cf = cf,
                presidio = presidio,
                indirizzoprincipale = indirizzoPrincipale,
                capprincipale = capPrincipale,
                comuneprincipale = comunePrincipale,
                seditot = sediTot,
                dipendenti = dipendenti,
                nlineetot = nLineeTot,
                fisso = fisso,
                mobile = mobile,
                totale = totale,
                fatturatocerved = fatturatoCerved,
                fatturatotim = fatturatoTim,
            )
        )
        print("tutto bvene")
    except Exception as error:
        print("rip")
        print(error)
        print(error.__cause__)
        conn.rollback()

    return redirect(url_for('.home',idPort = current_user.idport, id = idCliente))


@portafoglio_bp.route('/addTrattativaForm', methods=['POST'])
@login_required
def addTrattativaForm():
    try:
        print("addTrattattiva")
        print(current_user.get_id())
        print(type(current_user.get_id()))
        print(request.form['idClienteAdd'])
        print(request.form)
        idUtente = 2
        idCliente = request.form['idClienteAdd']
        codiceCtrDigitali = request.form['codiceCtrDigitaliAdd']
        codiceSalesHub = request.form['codiceSalesHubAdd']
        #areaManager = request.form['areaManagerAdd']
        zona = request.form['zonaAdd']
        tipo = request.form['tipoAdd']
        nomeOpportunita = request.form['nomeOpportunitaAdd']
        dataChiusuraOpportunita = request.form['dataCreazioneOpportunitaAdd']
        print("test data")
        print(dataChiusuraOpportunita)
        fix = checkNull(request.form['fixAdd'])
        mobile = checkNull(request.form['mobileAdd'])
        categoriaOffertaIT = request.form['categoriaOffertaITAdd']
        it = checkNull(request.form['itAdd'])
        lineeFoniaFix = checkNull(request.form['lineeFoniaFixAdd'])
        aom = checkNull(request.form['aomAdd'])
        mnp = checkNull(request.form['mnpAdd'])
        al = checkNull(request.form['alAdd'])
        dataChiusura = request.form['dataChiusuraAdd']
        fase = request.form['faseAdd']
        noteSpecialista = request.form['noteSpecialistaAdd']
        probabilita = request.form['probabilitaAdd']
        if not (probabilita is None):
            if("%" in probabilita):
                probabilita = probabilita[:-1]
        inPaf = request.form['inPafAdd']
        if (inPaf is None):
            inPaf = False
        fornitore = request.form['fornitoreAdd']
        
        conn.execute(insert(trattativa).values(
            idutente = current_user.get_id(),
            idcliente = idCliente,
            codicectrdigitali = codiceCtrDigitali,
            codicesaleshub = codiceSalesHub,
            areamanager = conn.execute(select(utente.c.areamanager).where(utente.c.idutente == current_user.get_id())).fetchone()[0],
            zona = zona,
            tipo = tipo,
            nomeopportunita = nomeOpportunita,
            datacreazioneopportunita = dataChiusuraOpportunita,
            fix = fix,
            mobile = mobile,
            categoriaoffertait = categoriaOffertaIT,
            it = it,
            lineefoniafix = lineeFoniaFix,
            aom = aom,
            mnp = mnp,
            al = al,
            datachiusura = dataChiusura,
            fase = fase,
            notespecialista = noteSpecialista,
            probabilita = probabilita,
            inpaf = 1,
            fornitore = fornitore
        ))
        
        print("tutto bene add")
    except Exception as error:
        print("rip")
        print(error)
        print(error.__cause__)
        conn.rollback()
    
    return redirect(url_for('.home',idPort = current_user.idport, id = idCliente))

@portafoglio_bp.route('/addItForm', methods=['POST'])
@login_required
def addItForm():
    try:
        print("addIt")
        #print(request.form)
        idCliente = request.form['idClienteAddIt']
        servizio = request.form['servizioAdd']
        quantita = checkNull(request.form['quantitaAdd'])
        tgu = request.form['tguAdd']
        dataAttivazione = checkDate(request.form['dataAttivazioneAdd'])
        dataScadenza = checkDate(request.form['dataScadenzaAdd'])
        canoneAnnuo = checkNull(request.form['canoneAnnuoAdd'])
        canoneMese = checkNull(request.form['canoneMeseAdd'])

        conn.execute(insert(it_table).values(
            idcliente = idCliente,
            servizio = servizio,
            quantita = quantita,
            tgu = tgu,
            dataattivazione = dataAttivazione,
            datascadenza = dataScadenza,
            canoneannuo = canoneAnnuo,
            canonemese = canoneMese
        ))
        
        print("tutto bene add")
    except Exception as error:
        print("rip")
        print(error)
        print(error.__cause__)
        conn.rollback()
    
    return redirect(url_for('.home',idPort = current_user.idport, id = idCliente))

@portafoglio_bp.route('/modifyIt/<int:id>', methods=['POST'])
def modifyIt(id):
    idcliente = request.form['idClienteModifyIt']
    servizio = request.form['servizioModify']
    quantita = request.form['quantitaModify']
    tgu = request.form['tguModify']
    dataattivazione = request.form['dataAttivazioneModify']
    datascadenza = request.form['dataScadenzaModify']
    canoneannuo = request.form['canoneAnnuoModify']
    canonemese = request.form['canoneMeseModify']

    try:
        conn.execute(update(it_table).values(
            servizio = servizio,
            quantita = quantita,
            tgu = tgu,
            dataattivazione = dataattivazione,
            datascadenza = datascadenza,
            canoneannuo = canoneannuo,
            canonemese = canonemese
        ).where(it_table.c.idit == id))
    except Exception as error:
        print("rip")
        print(error)
        print(error.__cause__)

    return redirect(url_for('.home', idPort = current_user.idport, id = idcliente))
@portafoglio_bp.route('/removeIt/<int:id>', methods=['POST'])
@login_required
def deleteIt(id):
    idcliente = 0
    try:
        idcliente= conn.execute(select(it_table.c.idcliente).where(it_table.c.idit == id)).fetchone()[0]
        conn.execute(delete(it_table).where(it_table.c.idit == id))
    except Exception as error:
        print("rip")
        print(error)
        print(error.__cause__)
    return redirect(url_for('.home', idPort = current_user.idport, id = idcliente))

@portafoglio_bp.route('/getExcel/<int:id>')
def getExcel(id):
    print("sto creando il file")
    print(id)
    res = conn.execute(select(cliente).where(cliente.c.idportafoglio == id)).fetchall()

    output = io.BytesIO()

    workbook = xlwt.Workbook()

    sh = workbook.add_sheet('Report Portafoglio')

    sh.write(0,0,'TIPO CLIENTE')
    sh.write(0,1,'CF')
    sh.write(0,2,'RAG_SOC_CLI')
    sh.write(0,3,'PRESIDIO')
    sh.write(0,4,'INDIRIZZO PRINCIPALE')
    sh.write(0,5,'COMUNE_PRINCIPALE')
    sh.write(0,6,'CAP_PRINCIPALE')
    sh.write(0,7,'PROVINCIA_DESCR_PRINCIPALE')
    sh.write(0,8,'PROVINCIA_SIGLA_PRINCIPALE')
    sh.write(0,9,'SEDI_TOT')
    sh.write(0,10,'N_LINEE_TOT')
    sh.write(0,11,'_FISSO')
    sh.write(0,12,'_MOBILE')
    sh.write(0,13,'_TOTALE')
    sh.write(0,14,'FATTURATO_CERVED')
    sh.write(0,15,'CLIENTE_OFF_MOB_SCADENZA')
    sh.write(0,16,'FATTURATO_IT_TIM')
    sh.write(0,17,'DIPENDENTI')

    idx = 0
    for row in res:
        print(row)
        sh.write(idx+1, 0, row['tipoCliente'])
        sh.write(idx+1, 1, row['cf'])
        sh.write(idx+1, 2, row['ragioneSociale'])
        sh.write(idx+1, 3, row['presidio'])
        sh.write(idx+1, 4, row['indirizzoPrincipale'])
        sh.write(idx+1, 5, row['comunePrincipale'])
        sh.write(idx+1, 6, row['capPrincipale'])
        sh.write(idx+1, 7, row['provinciaDescPrincipale'])
        sh.write(idx+1, 8, row['provinciaSiglaPrincipale'])
        sh.write(idx+1, 9, row['sediTot'])
        sh.write(idx+1, 10, row['nLineeTot'])
        sh.write(idx+1, 11, row['fisso'])
        sh.write(idx+1, 12, row['mobile'])
        sh.write(idx+1, 13, row['totale'])
        sh.write(idx+1, 14, row['fatturatoCerved'])
        sh.write(idx+1, 16, row['fatturatoTim'])
        sh.write(idx+1, 17, row['dipendenti'])
        idx += 1
    
    workbook.save(output)
    output.seek(0)
    
    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=report_portafoglio.xls"})
        
@portafoglio_bp.route('/getExcelTrattative/<int:id>')
def getExcelTrattative(id):
    print(id)
    res = conn.execute(select(trattativa)).fetchall()

    output = io.BytesIO()

    workbook = xlwt.Workbook()

    sh = workbook.add_sheet('Report Portafoglio')
    style0 = xlwt.easyxf('pattern: pattern solid, fore_colour red')
    sh.write(0,0,'CODICE CTR DIGITALE',style0)
    sh.write(0,1,'CODICE SALES HUB')
    sh.write(0,2,'AREA MANAGER')
    sh.write(0,3,'SA')
    sh.write(0,4,'RAGIONE SOCIALE')
    sh.write(0,5,'ZONA')
    sh.write(0,6,'TIPO')
    sh.write(0,7,'NOME OPPORTUNITA')
    sh.write(0,8,'DATA CREAZIONE OPPORTUNITA')
    sh.write(0,9,'FIX (€)')
    sh.write(0,10,'MOBILE(€)')
    sh.write(0,11,'CATEGORIA OFFERTA IT')
    sh.write(0,12,'IT')
    sh.write(0,13,'LINEE FONIA FIX')
    sh.write(0,14,'AOM')
    sh.write(0,15,'MNP')
    sh.write(0,16,'AL')
    sh.write(0,17,'DATA CHIUSURA')
    sh.write(0,18,'FASE')
    sh.write(0,19,'NOTE SPECIALISTA')
    sh.write(0,20,'PROBABILITA')
    sh.write(0,21,'IN PAF')
    sh.write(0,22,'FORNITORE')

    idx = 0
    for row in res:
        print(row)
        sh.write(idx+1, 0, row['codiceCtrDigitali'])
        sh.write(idx+1, 1, row['codiceSalesHub'])
        sh.write(idx+1, 2, row['areaManager'])
        sh.write(idx+1, 3, 'SALVATORE IACCARINO')
        sh.write(idx+1, 4, 'NOME CLIENTE')
        sh.write(idx+1, 5, row['zona'])
        sh.write(idx+1, 6, row['tipo'])
        sh.write(idx+1, 7, row['nomeOpportunita'])
        sh.write(idx+1, 8, row['dataCreazioneOpportunita'])
        sh.write(idx+1, 9, row['fix'])
        sh.write(idx+1, 10, row['mobile'])
        sh.write(idx+1, 11, row['categoriaOffertaIT'])
        sh.write(idx+1, 12, row['it'])
        sh.write(idx+1, 13, row['lineeFoniaFix'])
        sh.write(idx+1, 14, row['aom'])
        sh.write(idx+1, 15, row['mnp'])
        sh.write(idx+1, 16, row['al'])
        sh.write(idx+1, 17, row['dataChiusura'])
        sh.write(idx+1, 18, row['fase'])
        sh.write(idx+1, 19, row['noteSpecialista'])
        sh.write(idx+1, 20, row['probabilita'])
        sh.write(idx+1, 21, row['inPaf'])
        sh.write(idx+1, 22, row['fornitore'])
        idx += 1


    workbook.save(output)
    output.seek(0)
    
    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=pipeline.xls"})
   
""""
  idUtente = current_user.get_id(),
                idPortafoglio = lastPortafoglio,
                tipoCliente = 1,
                cf = correctValue(list[1],
                ragioneSociale = correctValue(list[2]),
                presidio = 1,
                indirizzoPrincipale = correctValue(list[4]),
                comunePrincipale = 1,
                capPrincipale = correctValue(list[6]),
                provinciaDescPrincipale = correctValue(list[7]),
                provinciaSiglaPrincipale = correctValue(list[8]),
                sediTot = correctValue(list[9]),
                nLineeTot = correctValue(list[10]),
                fisso = correctValue(list[11]),
                mobile = correctValue(list[12]),
                totale = correctValue(list[12]),
                fatturatoCerved = correctValue(list[13]),
                fatturatoTim = correctValue(list[15]),
                dipendenti = correctValue(list[16])"""