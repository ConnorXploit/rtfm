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

def nuevoGasto(nombre, cantidad, compartido, debe):
    try:        
        user_id = session['user_id']
        db = get_db()
        db.execute('insert into gasto (user_id, nombre, cantidad, pagado, compartido, debe) values (?, ?, ?, ?, ?, ?)', [user_id, nombre, float(cantidad), 0, 1 if compartido else 0, debe])
        db.commit()
        return True
    except Exception as e:
        log.send(str(e), 'EXCEPTION')
        return False

def pagarGasto(gasto_id):
    try:
        db = get_db()
        db.execute("update gasto set pagado = 1 where id = ?", [gasto_id])
        db.commit()
        return nombreGasto(gasto_id)
    except Exception as e:
        log.send(str(e))
        return False

def nombreGasto(gasto_id):
    try:
        db = get_db()
        cur = db.execute("select nombre from gasto where id = ?", [gasto_id])
        return cur.fetchall()[0]['nombre']
    except Exception as e:
        log.send(str(e))
        return None

def listaGastos():
    try:
        db = get_db()
        cur = db.execute( """select u.name as user, gasto.id as id, nombre, sum(cantidad) as cantidad, pagado, compartido, a.name as debe
         from gasto
         inner join user u on u.id = gasto.user_id
         inner join user a on a.id = gasto.debe
		 group by nombre, debe, cantidad
         order by gasto.id desc""" )
        return cur.fetchall()
    except Exception as e:
        log.send(str(e), 'EXCEPTION')
        return None

def debenGasto(nombre, cantidad):
    try:
        db = get_db()
        cur = db.execute(f"""select u.name as nombre
            from gasto
            inner JOIN
                user u
                    on u.id = gasto.debe
            where pagado = 0
            and nombre = '{nombre}'
            and cantidad = {cantidad}
            group by debe""")
        usuarios = []
        for user in cur:
            usuarios.append(user['nombre'])
        return usuarios
    except Exception as e:
        log.send(str(e))
        return None

def cuantoDebo():
    try:
        if 'username' in session:
            db = get_db()
            usuarios = listaUsuarios()
            cur = db.execute("""select u.name as nombre, sum(cantidad) as cantidad, pagado, c.name as debe, compartido
                from gasto
                    inner join 
                        user u
                            on u.id = gasto.user_id 
                    inner join 
                        user c
                            on c.id = gasto.debe
                where pagado = 0
                group by user_id, compartido, pagado, compartido, debe""")

            cuenta_usuarios = {}
            for pagos_user in cur:
                if pagos_user['nombre'] == session['username']:
                    if not pagos_user['debe'] in cuenta_usuarios:
                        cuenta_usuarios[pagos_user['debe']] = 0.00
                    cuenta_usuarios[pagos_user['debe']] -= pagos_user['cantidad']
                    # cuenta -= pagos_user['cantidad']
                else:
                    if pagos_user['debe'] == session['username']:
                        if not pagos_user['nombre'] in cuenta_usuarios:
                            cuenta_usuarios[pagos_user['nombre']] = 0.00
                        cuenta_usuarios[pagos_user['nombre']] += pagos_user['cantidad']
            return cuenta_usuarios
    except Exception as e:
        log.send(str(e))
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

def listaUsuarios():
    # Cogemos todos los nombres de usuarios
    if 'user_id' in session:
        db = get_db()
        cur = db.execute("select id, name from user where id != {n}".format(n=session['user_id']))
        return cur.fetchall()

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

def dameMiID():
    try:
        db = get_db()
        cur = db.execute("select id from user where name = '{n}'".format(n=session['username']))
        return cur.fetchall()[0]['id']
    except Exception as e:
        log.send(str(e), 'EXCEPTION')
    return False

def dameID(username):
    try:
        db = get_db()
        cur = db.execute("select id from user where name = '{n}'".format(n=username))
        return cur.fetchall()[0]['id']
    except Exception as e:
        log.send(str(e), 'EXCEPTION')
    return False

def dameNombre(id):
    try:
        db = get_db()
        cur = db.execute("select name from user where id = {n}".format(n=id))
        return cur.fetchall()[0]['name']
    except Exception as e:
        log.send(str(e), 'EXCEPTION')
    return False

def loginBBDD(name, password):
    try:
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
            session['user_id'] = user_id
            session['username'] = name
    except Exception as e:
        log.send(str(e), 'EXCEPTION')

def logoutBBDD():
    # for session_type in SESSION_TYPES:
    #     session.pop(session_type, None)
    session.clear()