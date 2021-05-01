# encoding: utf-8
from .rtfm import get_db, session, log, datetime
import hashlib, socket

SESSION_TYPES = [
    'hacker',
    'user_id',
    'username'
]

# Schedules

def crearSchedule(scheduleName, scheduleInfo, userId):
    try:
        db = get_db()
        cur = db.execute('select schedule_name from schedule order by id asc')
        entries = cur.fetchall()

        existe = False
        for entry in entries:
            if entry['schedule_name'] == scheduleName:
                existe = True

        if existe:
            log.send('El schedule ya existía')
            return False

        fecha = datetime.now().strftime('%Y/%m/%d - %H:%M')

        db.execute('insert into schedule (schedule_name, schedule_info, user_id, date) values (?, ?, ?, ?)', [scheduleName, scheduleInfo, userId, fecha])
        db.commit()

        return True
    except Exception as e:
        log.send(str(e), 'EXCEPTION')
        return False

def getScheduleID(scheduleName):
    try:
        db = get_db()
        cur = db.execute( "select id from schedule where schedule_name = '{n}'".format(n=scheduleName) )
        return cur.fetchall()[0]['id']
    except Exception as e:
        log.send(str(e), 'EXCEPTION')
        return None

# Calendar

def agregarEvento(eventName, startDate, endDate):
    try:
        db = get_db()
        db.execute('insert into event (event_text, date_start, date_end) values (?, ?, ?)', [eventName, startDate, endDate])
        db.commit()
        return True
    except Exception as e:
        log.send(str(e), 'EXCEPTION')
        return False

def listaEventos():
    try:
        db = get_db()
        cur = db.execute( "select * from event" )
        return cur.fetchall()
    except Exception as e:
        log.send(str(e), 'EXCEPTION')
        return None

def eliminaEvento(eventID):
    try:
        db = get_db()
        db.execute('delete from event where id = ?', [eventID])
        db.commit()
        return True
    except Exception as e:
        log.send(str(e), 'EXCEPTION')
        return False

# Gastos

def nuevoGasto(nombre, cantidad):
    try:        
        user_id = session['user_id']
        db = get_db()
        db.execute('insert into gasto (user_id, nombre, cantidad) values (?, ?, ?)', [user_id, nombre, float(cantidad)])
        db.commit()
        return True
    except Exception as e:
        raise
        log.send(str(e), 'EXCEPTION')
        return False

def pagarGasto(gasto_id):
    try:
        db = get_db()
        db.execute("update gasto set pagado = 1 where id = ?", [gasto_id])
        db.commit()
        return True
    except:
        return False

def listaGastos():
    try:
        db = get_db()
        cur = db.execute( "select * from gasto where pagado = 0 order by id desc" )
        return cur.fetchall()
    except Exception as e:
        log.send(str(e), 'EXCEPTION')
        return None

# Session

def crearUsuario(name, password, telegram, verify_code, fecha_creacion):
    # Cogemos todos los nombres de usuarios
    db = get_db()
    cur = db.execute('select name from user order by id desc')
    entries = cur.fetchall()

    # Verificamos si existe
    existe = False
    for entry in entries:
        if entry['name'] == name:
            existe = True

    if existe:
        return False

    # Transformamos la password a MD5
    password = hashlib.md5( password.encode() ).digest()

    # Insertamos en BBDD
    db.execute('insert into user (name, password, verify_code, telegram, fecha_creacion) values (?, ?, ?, ?, ?)', [name, password, verify_code, telegram, fecha_creacion])
    db.commit()
    
    return True

def usuarioVerificado(telegram):
    # Cogemos todos los nombres de usuarios
    db = get_db()
    cur = db.execute("select verify_code from user where telegram = '{n}'".format(n=telegram))
    if cur.fetchall()[0]['verify_code'] != 'VERIFIED':
        return False
    return True

def regenerarVerificacion(telegram, verify_code, fecha_creacion):
    try:
        db = get_db()
        db.execute("update user set verify_code = '{ver}', fecha_creacion = '{fech}' where telegram = '{telegram}'".format(ver=verify_code, fech=fecha_creacion, telegram=telegram))
        db.commit()
        return True
    except:
        return False

def verificarCodigo(telegram, verify_code):
    try:
        db = get_db()
        cur = db.execute("select verify_code from user where telegram = '{n}'".format(n=telegram))
        if cur.fetchall()[0]['verify_code'] == verify_code:
            db.execute("update user set verify_code = 'VERIFIED' where telegram = '{telegram}'".format(telegram=telegram))
            db.commit()
            return True
    except:
        pass
    return False

def loginBBDD(name, password):
    db = get_db()
    password = hashlib.md5( password.encode() ).digest()
    resp = db.execute("select id from user where name = ? and password = ? and verify_code = ?", [name, password, 'VERIFIED'])
    respuesta = resp.fetchall()
    if len(respuesta) == 0:
        pass
    else:
        session['hacker'] = True
        user_id = -1
        for entry in respuesta:
            user_id = entry['id']
        log.send('inicia sesion {n}'.format(n=user_id))
        session['user_id'] = user_id
        session['username'] = name

def logoutBBDD():
    for session_type in SESSION_TYPES:
        session.pop(session_type, None)