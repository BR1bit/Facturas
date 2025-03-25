# 📬 Envío Automático de Recibos PDF por Correo

Este proyecto en Flask permite a una organización cargar un archivo Excel con datos personales (nombre, documento y email) y un único archivo PDF que contiene **múltiples recibos**. La aplicación:

- 📄 Divide el PDF por página
- 🔍 Extrae el número de documento (C.I.)
- 🧾 Cruza con el Excel
- 📬 Envía el recibo correspondiente por email al destinatario
- 📝 Genera un log de envío
- 📤 Envía el log por correo al administrador

---

## 🚀 Cómo ejecutar localmente

### Requisitos

- Python 3.9+
- pip

### Instalación

```bash
git clone https://github.com/BR1bit/Facturas.git
cd Facturas
pip install -r requirements.txt
```

### Ejecutar la app

```bash
python app.py
```

La aplicación estará disponible en [http://localhost:8080](http://localhost:8080)

---

## 🧰 Estructura del proyecto

```
Facturas/
├── app.py                 # Lógica principal del servidor Flask
├── templates/
│   ├── index.html         # Formulario de carga
│   └── resultado.html     # Resumen del envío
├── static/
│   └── log_envio_*.txt    # Logs generados por cada envío (temporales)
├── requirements.txt       # Dependencias
├── fly.toml               # Configuración para desplegar en Fly.io
├── Dockerfile             # Imagen base para despliegue
└── README.md              # Este archivo
```

---

## 🧾 Formato del Excel esperado

El archivo Excel debe tener al menos estas columnas:

- **Nombre**
- **Documento** (solo números, sin puntos ni guiones)
- **Email**

Ejemplo:

| Nombre             | Documento | Email                |
|--------------------|-----------|----------------------|
| Juan Pérez         | 43153054  | juan@dominio.com     |

---

## 🧪 Formato del PDF

Debe contener **una o más páginas**, cada una con un recibo. El sistema busca una línea tipo:

```
C.I. 4.315.305-4
```

y extrae el documento para vincularlo con el Excel.

---

## 📦 Despliegue en Fly.io

### 1. Iniciar Fly.io

```bash
fly launch
```

### 2. Crear y configurar secretos

```bash
fly secrets set CONTRASENA="clave_de_app_de_gmail"
```

### 3. Desplegar

```bash
fly deploy
```

---

## 💡 Funciones adicionales

- Envía `log_envio.txt` automáticamente a `recibos@apes.edu.uy`
- Usa `pdfplumber` para extracción de texto confiable
- Usa `PyPDF2` para generar PDF individuales por recibo
- Soporta comparación aproximada de nombres (`fuzzy matching`) para emparejar con Excel

---

## 📧 Contacto

Creado por **Bruno Rodríguez**  
📬 recibos@apes.edu.uy

---

## ✅ Licencia

Este proyecto se distribuye bajo licencia MIT.
