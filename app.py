from flask import Flask, request, render_template
import os
import tempfile
import pandas as pd
import pdfplumber
import smtplib
from email.message import EmailMessage
import re
from datetime import datetime
from PyPDF2 import PdfWriter, PdfReader

app = Flask(__name__)

# Configurar correo
CORREO_ORIGEN = "recibos@apes.edu.uy"
CONTRASENA = "ovln ktsb vmti bwpy"
DESTINATARIO_LOG = "recibos@apes.edu.uy"

# Función para buscar el documento en el texto
def buscar_documento(texto):
    match = re.search(r'C\.I\.*\s*([0-9.\-]+)', texto, re.IGNORECASE)
    if match:
        documento_crudo = match.group(1)
        return re.sub(r'\D', '', documento_crudo).strip()
    return None

# Enviar correo con archivo adjunto
def enviar_correo(destinatario, asunto, cuerpo, archivo_adjunto):
    msg = EmailMessage()
    msg['Subject'] = asunto
    msg['From'] = CORREO_ORIGEN
    msg['To'] = destinatario
    msg.set_content(cuerpo)

    with open(archivo_adjunto, 'rb') as f:
        contenido = f.read()
        msg.add_attachment(contenido, maintype='application', subtype='pdf', filename=os.path.basename(archivo_adjunto))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(CORREO_ORIGEN, CONTRASENA)
        smtp.send_message(msg)

# Enviar el log final al correo administrador
def enviar_log_a_admin(ruta_log):
    asunto = "📋 Log de Envío de Recibos"
    cuerpo = "Adjuntamos el log con el resumen del proceso de envío de recibos."
    enviar_correo(DESTINATARIO_LOG, asunto, cuerpo, ruta_log)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        excel = request.files['excel']
        pdf_file = request.files['pdf']

        temp_dir = tempfile.mkdtemp()
        excel_path = os.path.join(temp_dir, 'lista.xlsx')
        pdf_dir = os.path.join(temp_dir, 'pdfs')
        os.mkdir(pdf_dir)

        excel.save(excel_path)
        pdf_path = os.path.join(temp_dir, pdf_file.filename)
        pdf_file.save(pdf_path)

        # Leer Excel y limpiar los documentos
        df = pd.read_excel(excel_path)
        df["Documento"] = df["Documento"].astype(str).str.replace(r'\D', '', regex=True).str.strip()

        # Preparar log y contadores
        enviados = 0
        fallidos = []
        log_lines = []
        log_lines.append(f"=== LOG DE ENVÍO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

        pdf_reader = PdfReader(pdf_path)

        with pdfplumber.open(pdf_path) as pdf:
            for i, pagina in enumerate(pdf.pages):
                texto = pagina.extract_text() or ""
                doc_encontrado = buscar_documento(texto)
                log_lines.append(f"📄 Página {i+1}")
                log_lines.append(f"📎 Documento detectado: {doc_encontrado}")
                log_lines.append(f"📝 Texto extraído (Página {i+1}): {texto[:200]}...")

                if doc_encontrado and df["Documento"].str.contains(doc_encontrado).any():
                    fila = df[df["Documento"].str.contains(doc_encontrado)].iloc[0]
                    nombre = fila["Nombre"]
                    correo = fila["Email"]

                    writer = PdfWriter()
                    writer.add_page(pdf_reader.pages[i])
                    temp_page_path = os.path.join(pdf_dir, f"pagina_{i+1}.pdf")
                    with open(temp_page_path, "wb") as f:
                        writer.write(f)

                    try:
                        enviar_correo(
                            destinatario=correo,
                            asunto="Tu recibo",
                            cuerpo=f"Hola {nombre}, adjunto te enviamos tu recibo.\n\nSaludos.",
                            archivo_adjunto=temp_page_path
                        )
                        enviados += 1
                        log_lines.append(f"✅ Enviado a {correo} (Nombre: {nombre})\n")
                    except Exception as e:
                        error_msg = f"❌ ERROR al enviar a {correo}: {str(e)}\n"
                        log_lines.append(error_msg)
                        fallidos.append((correo, str(e)))
                else:
                    motivo = "Documento no encontrado en el texto o no está en el Excel"
                    log_lines.append(f"❌ Página {i+1} no enviada: {motivo}\n")
                    fallidos.append((f"pagina_{i+1}.pdf", motivo))

        # Guardar log
        log_path = os.path.join("static", f"log_envio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(log_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write("\n".join(log_lines))

        # Enviar log al administrador
        enviar_log_a_admin(log_path)

        return render_template('resultado.html', enviados=enviados, fallidos=fallidos, log_path=log_path)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
