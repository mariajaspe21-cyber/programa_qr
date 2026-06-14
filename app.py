from flask import Flask, render_template, request, redirect, url_for, session
import qrcode
import io
import base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'llave_sistema_qr_profesional_y_completo'

def verificar_estructuras():
    if 'LISTA_PERSONAS' not in session:
        session['LISTA_PERSONAS'] = []
    if 'HISTORIAL_ASISTENCIAS' not in session:
        session['HISTORIAL_ASISTENCIAS'] = []

@app.route('/', methods=['GET', 'POST'])
def index():
    verificar_estructuras()
    qr_base64 = None
    persona_registrada = None

    if request.method == 'POST':
        # ACCIÓN DEL ADMINISTRADOR: Recibe la información y genera el QR
        if 'btn_generar_qr' in request.form:
            nombre = request.form.get('nombre').strip()
            id_usuario = request.form.get('id_usuario').strip()
            telefono = request.form.get('telefono').strip()
            cedula = request.form.get('cedula').strip()

            persona_registrada = {
                "nombre": nombre,
                "id": id_usuario,
                "telefono": telefono,
                "cedula": cedula
            }

            # Guardamos en la memoria del sistema
            lista = session['LISTA_PERSONAS']
            lista.append(persona_registrada)
            session['LISTA_PERSONAS'] = lista

            # Empaquetamos los datos solicitados
            datos_qr = f"ACCESO_VALIDO|ID:{id_usuario}|NOM:{nombre}|TEL:{telefono}|CI:{cedula}"
            
            # Generación técnica del QR
            qr = qrcode.QRCode(version=1, box_size=8, border=4)
            qr.add_data(datos_qr)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#0f172a", back_color="white")
            
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            session.modified = True

        # ACCIÓN DEL QUE NECESITA REPORTAR: Simula lectura óptica
        elif 'btn_reportar_asistencia' in request.form:
            persona_index = int(request.form.get('persona_seleccionada'))
            if persona_index < len(session['LISTA_PERSONAS']):
                persona = session['LISTA_PERSONAS'][persona_index]
                
                # Registramos en el log agregando el estado de autorización
                historial = session['HISTORIAL_ASISTENCIAS']
                historial.append({
                    "id": persona['id'],
                    "nombre": persona['nombre'],
                    "cedula": persona['cedula'],
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "hora": datetime.now().strftime("%I:%M:%S %p"),
                    "estado": "Autorizado"  # Estado dinámico recomendado
                })
                session['HISTORIAL_ASISTENCIAS'] = historial
                session.modified = True

    # Calculamos el total de registros para el contador del supervisor
    total_asistencias = len(session['HISTORIAL_ASISTENCIAS'])

    return render_template('index.html', 
                           personas=session['LISTA_PERSONAS'], 
                           reportes=session['HISTORIAL_ASISTENCIAS'], 
                           qr_code=qr_base64,
                           ultima_persona=persona_registrada,
                           total_asistencias=total_asistencias)

@app.route('/limpiar')
def limpiar():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)