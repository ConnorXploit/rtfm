# encoding: utf-8
# Todos los imports
import os, json, hashlib, requests, threading, dateutil.relativedelta, time
from requests_toolbelt.multipart.encoder import MultipartEncoder
from datetime import datetime, timedelta
from random import choice, randint
from threading import Thread
from flask import Flask, request, session, redirect, url_for, abort, render_template, flash, jsonify, current_app, send_file
import urllib3
from . import telegram
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Creamos la instancia de la aplicación
app = Flask(__name__)

# Cargamos la configuración desde este fichero, pecera.py
app.config.from_object(__name__)

# Iniciamos un mensaje de telegram
telegram_bot = telegram.Bot()
#telegram_bot.sendMessage('Servidor RTFM iniciado - {tiempo}'.format(tiempo=datetime.now()))

# Cargamos los valores de la configuración
from .config import DIR_ACTUAL, frases, global_conf
from .config import connect_db, get_db, close_db, init_db, initdb_command
from .logger import Logger

log = Logger(DIR_ACTUAL)

# Cargamos las APIs
from . import APIS

# Threads
class FlaskThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = current_app._get_current_object()

    def run(self):
        with self.app.app_context():
            super().run()

# Cargamos las funciones de la BBDD
from .database import loginBBDD, logoutBBDD
from .database import crearUsuario, usuarioVerificado, regenerarVerificacion, verificarCodigo, listaUsuarios, dameNombre
from .database import agregarEvento, eliminaEvento, listaEventos
from .database import nuevoGasto, pagarGasto, listaGastos, nombreGasto, cuantoDebo
from .database import listaProductos, nuevoActualizaProducto

# Directorio actual
DIR_ACTUAL = os.path.dirname(os.path.realpath(__file__))

from .background import schedule

BACKGROUND_PROCESSES = [
    #[ 'DATABASE_UPDATE_CVES', schedule, (app.config['DATABASE_UPDATE_SCHEDULE'], updateCveDataBase,) ]
]

for backProcess in BACKGROUND_PROCESSES:
    with app.app_context():
        log.send('Loading background process for {f}'.format(f=backProcess[0]), 'BACKGROUND')
        scan = FlaskThread( target=backProcess[1], args=backProcess[2] )
        scan.daemon = True
        scan.start()

NEEDED_FOLDERS = [
    app.config['UPLOAD_PATH'],
    app.config['DOWNLOAD_PATH']
]

for folder in NEEDED_FOLDERS:
    if not os.path.isdir(folder):
        os.mkdir(folder)

def verify_code(telegram):
    if not usuarioVerificado(telegram):
        verifycation_code = '-'.join( [ str(randint(1000, 9999)), str(randint(1000, 9999)), str(randint(1000, 9999)), str(randint(1000, 9999)) ] )
        fecha_creacion = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        if regenerarVerificacion(telegram, verifycation_code, fecha_creacion):
            hora = datetime.now() + timedelta(minutes=global_conf['INDEX']['CHECK_VERIFY_CODE_MINUTES'])
            hora = hora.strftime('%H:%M')
            telegram_bot.sendMessage('{tele} se te ha caducado el codigo. El nuevo código de verificación de tu cuenta es: {cod}. ¡Tendrás {min} minutos para validar la sesión!'.format(tele=telegram, cod=verifycation_code, min=global_conf['INDEX']['CHECK_VERIFY_CODE_MINUTES']))
            log.send('Loading background process for VERIFY_CODE_USER', 'BACKGROUND')
            scan = FlaskThread( target=schedule, args=(hora, verify_code, telegram, True ) )
            scan.daemon = True
            scan.start()

# Inicio
@app.route('/')
def inicio():
    try:
        session_iniciada = 'hacker' in session
        frase = choice(frases)
        gastos = listaGastos()
        otrosUsuarios = listaUsuarios()
        if not gastos:
            gastos = []
        cuanto = cuantoDebo()
        if not cuanto:
            cuanto = {}
        return render_template('index.html', frase=frase, gastos=gastos, cuantoDebo=cuanto, otrosUsuarios=otrosUsuarios, session_iniciada=session_iniciada)
    except Exception as e:
        log.send( str(e), 'EXCEPTION' )

    return render_template('index.html')

# Calendario
@app.route('/addevent', methods=['POST'])
def addevent():
    creado = False
    try:
        addEventText = request.form.get('addEventText')
        fechaEventText = request.form.get('fechaEventText')
        if fechaEventText:
            date_start = fechaEventText.split(' - ')[0]
            date_end = fechaEventText.split(' - ')[-1]
            creado = agregarEvento(addEventText, date_start, date_end)
            if date_start == date_end:
                log.send('Se ha añadido el evento {nombre} para el dia {da}'.format(nombre=addEventText, da=date_start), "CALENDARIO")
            else:
                log.send('Se ha añadido el evento {nombre} del dia {da} al dia {da2}'.format(nombre=addEventText, da=date_start, da2=date_end), "CALENDARIO")
    except Exception as e:
        log.send( str(e), 'EXCEPTION' )

    return jsonify({'creado' : creado})

@app.route('/events', methods=['GET'])
def events():
    try:
        eventos = listaEventos()
        datos = []
        for evento in eventos:
            valores = {}
            valores['title'] = evento['event_text']
            valores['start'] = evento['date_start']
            valores['end'] = evento['date_end']
            if not valores['end']:
                del valores['end']
            datos.append( valores )
    except Exception as e:
        log.send( str(e), 'EXCEPTION' )

    return jsonify(datos)

# Gastos
@app.route('/addgasto', methods=['POST'])
def addgasto():
    creado = False
    try:
        addGastoText = request.form.get('addGastoText')
        addGastoCantidad = float(request.form.get('addGastoCantidad'))
        usuariosGasto = request.form.getlist('compartido')
        compartido = 'compartido' in request.form
        gastos = []
        usuarios = []
        for usuario in usuariosGasto:
            if int(usuario) is not session['user_id']:
                creado = nuevoGasto(addGastoText, round(addGastoCantidad/len(usuariosGasto), 2), compartido, usuario)
                if creado:
                    user_temp = dameNombre(usuario)
                    usuarios.append(user_temp)
                    gastos.append({ 'creado' : creado, 'cantidad': round(addGastoCantidad/len(usuariosGasto), 2), 'debe': user_temp })
        if gastos:
            log.send(f'Se ha añadido el gasto para {", ".join(usuarios)} de {addGastoText} con un precio de {addGastoCantidad}€', "GASTO")
    except Exception as e:
        log.send( str(e), 'EXCEPTION' )

    return jsonify({'gastos' : gastos})
    
@app.route('/pagar/<int:gasto>', methods=['POST'])
def pagar(gasto):
    pagado = False
    try:
        producto = pagarGasto(gasto)
        if producto:
            log.send('Se ha pagado el gasto {nombre}'.format(nombre=producto), "GASTO")
            pagado = True
    except Exception as e:
        log.send( str(e), 'EXCEPTION' )

    return jsonify({'creado' : pagado})

@app.route('/cuantoDebo', methods=['GET'])
def cuanto():
    return jsonify({'cuantoDebo' : cuantoDebo()})

# Productos
@app.route('/farmacia')
def farmacia():
    try:
        session_iniciada = 'hacker' in session
        productos = listaProductos()
        frase = choice(frases)
        if not productos:
            productos = []
        return render_template('productos.html', frase=frase, productos=productos, session_iniciada=session_iniciada)
    except Exception as e:
        log.send( str(e), 'EXCEPTION' )

    return render_template('index.html')

@app.route('/actualizarproducto', methods=['POST'])
def actualizarProducto():
    try:
        values = request.get_json()
        producto = values.get('producto')
        cantidad = values.get('cantidad')

        if cantidad == 0:
            return jsonify({'error' : 'non-zero-value'})

        try:
            cantidad = int(cantidad)
        except:
            return jsonify({'error' : 'non-int-value'})

        cantidad_antes = cantidad * -1

        actualizado, existia, quedan, cantidad = nuevoActualizaProducto(producto, cantidad)

        msg = ''
        error = None

        if actualizado:
            if existia:
                if quedan:
                    msg = f'Se ha actualizado el fármaco {producto} y ahora hay {cantidad} pilulas'

                else:
                    msg = f'Se ha actualizado el fármaco {producto} y ahora quedan solo {cantidad} pilulas... Mejor si compras'

            else:
                msg = f'Se ha añadido el fármaco {producto} con la cantidad de {cantidad} pilulas'

        else:
            if existia:
                error = f"No se pueden coger {cantidad_antes} pilulas... Solo hay {cantidad}"
            else:
                error = 'error-cant-create-or-update'

        if error:
            log.send(error, 'ERROR')
            return jsonify({'error' : error})

        log.send(msg, "FARMACIA")
        return jsonify({'result' : msg})

    except Exception as e:
        log.send( str(e), 'EXCEPTION' )
        return jsonify({'error' : str(e)})

# Sesiones
@app.route('/signup', methods=['POST'])
def signup():
    creado = False
    try:
        nombre = request.form['username']
        password = request.form['password']  
        telegram = request.form['telegram']

        if not '@' in str(telegram)[0]:
            telegram = '@' + str(telegram)

        verifycation_code = '-'.join( [ str(randint(1000, 9999)), str(randint(1000, 9999)), str(randint(1000, 9999)), str(randint(1000, 9999)) ] )

        fecha_creacion = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        creado = crearUsuario( nombre, password, telegram, verifycation_code, fecha_creacion )

        if creado:
            hora = datetime.now() + timedelta(minutes=global_conf['INDEX']['CHECK_VERIFY_CODE_MINUTES'])
            hora = hora.strftime('%H:%M')
            telegram_bot.sendMessage('{tele} el código de verificación de tu cuenta es: {cod}. ¡Tendrás {min} minutos para validar la sesión!'.format(tele=telegram, cod=verifycation_code, min=global_conf['INDEX']['CHECK_VERIFY_CODE_MINUTES']))
            with app.app_context():
                log.send('Loading background process for VERIFY_CODE_USER', 'BACKGROUND')
                scan = FlaskThread( target=schedule, args=(hora, verify_code, telegram, True ) )
                scan.daemon = True
                scan.start()

    except Exception as e:
        log.send( str(e), 'EXCEPTION' )

    return jsonify({'creado' : creado})

@app.route('/validatesignup', methods=['POST'])
def validatesignup():
    validado = False
    try: 
        telegram = request.form['telegramverify'] 
        verifycation_code = request.form['verify_code']
        if verificarCodigo(telegram, verifycation_code):
            telegram_bot.sendMessage('{tele} ¡Cuenta registrada correctamente!'.format(tele=telegram))
            validado = True
    except Exception as e:
        log.send( str(e), 'EXCEPTION' )
    return jsonify({'validado' : validado})

@app.route('/login', methods=['POST'])
def login():
    try:
        if request.method == 'POST':
            usuario = request.form['username']
            password = request.form['password']
            loginBBDD( usuario, password )
    except Exception as e:
        log.send( str(e), 'EXCEPTION' )
    return redirect(url_for('inicio'))

@app.route('/logout')
def logout():
    try:
        logoutBBDD()
    except Exception as e:
        log.send( str(e), 'EXCEPTION' )
    return redirect(url_for('inicio'))
