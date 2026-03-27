![FastAPI](https://img.shields.io/badge/FastAPI-0.128.3-000000?style=for-the-badge&logo=fastapi )
![Python](https://img.shields.io/badge/python-3.11.9-000000?style=for-the-badge&logo=Python&logoColor=)
![Pydantic](https://img.shields.io/badge/Pydantic-2.12.5-000000?style=for-the-badge&logo=pydantic)
![Jinja](https://img.shields.io/badge/Jinja2-3.1.6-000000?style=for-the-badge&logo=jinja)
![Posgresql](https://img.shields.io/badge/Postgresql-9.9-000000?style=for-the-badge&logo=postgresql&logoColor=white)
![js](https://img.shields.io/badge/javascript-ES6+-000000?style=for-the-badge&logo=javascript)
![WebSocket](https://img.shields.io/badge/websocket-16.0-000000?style=for-the-badge&logo=websocket)
![Alembic](https://img.shields.io/badge/Alembic-1.18.0-000000?style=for-the-badge&logo=alembic)
![Html](https://img.shields.io/badge/html-000000?style=for-the-badge&logo=html5)
![Css](https://img.shields.io/badge/Css-000000?style=for-the-badge&logo=css)
![Google Gemini](https://img.shields.io/badge/Gemini-000000?style=for-the-badge&logo=googlecloud)

# ProntoERP

Este sistema ERP multi-tenancy busca solucionar problemas comunes de fabricas y distribuidoras de muebles sueltos y sobre medida, tiene control de inventario, control de producción en fabrica, proyectos separados por ambiente y/o cliente, con la posibilidad de compartir un enlace para que el cliente pueda dar seguimiento a su pedido en tiempo real ofreciendo total transparencia al cliente y arquitectos, ayuda al seguimiento de las finanzas de la empresa donde se pueden ver distintos graficos y tablas para analizar los ingresos/gastos/lucros de una empresa y organizarlos por tipo, todo eso con ayuda de un agente IA que usa el motor de Gemini para ejecutar tareas y ayudar a los usuarios con sus dudas, la aplicacion cuenta con un sistema WebSocket para mostrar notificaciones en tiempo real y que toda los usuarios esten por dentro de las decisiones y actividades dentro de su trabajo

---

## 📸 Vista previa

![Home](https://i.imgur.com/Z89LSHn.png)

![Login](https://i.imgur.com/Z8B7FX5.png)

![Signup](https://i.imgur.com/SBVbcZB.png)

![Inventory](https://i.imgur.com/h0xzs4F.png)

![Verify Email](https://i.imgur.com/hvAY55S.png)

![Notifications](https://i.imgur.com/lZjmEA6.png)

---

## 🧠 Descripción

Este proyecto busca resolver:

Este sistema permite a pequeñas y medianas carpinterias y negocios del sector mobiliario gestionar stock, contactos, producción, finanzas y proyectos en un solo lugar, reduciendo errores humanos, mejorando trazabilidad, comunicación y dando la oportunidad a los carpinteros de poder concentrarse mas en su trabajo sin perder tiempo ni energia en logistica y burocracias al mantener el contacto con el cliente de una forma mas facíl y satisfactoria para el usuario



## ⚙️ Tecnologías usadas

#### Backend & API
+ FastAPI
+ Uvicorn
+ Starlette

#### Base de Datos & ORM
+ SQLAlchemy
+ Alembic
+ PostgreSQL (psycopg2)

#### Seguridad & Autenticación
+ JWT (python-jose)
+ Passlib (Bcrypt)
+ Cryptography

#### Validación & Configuración
+ Pydantic
+ Pydantic-Settings
+ Python-dotenv

#### Comunicación & Utilidades
+ FastAPI-Mail (aiosmtplib)
+ Jinja2
+ AnyIO
+ Websockes
---

## 🏗️ Estructura del proyecto
```
erm/
│
├── core/
│   ├── main.py
│   ├── database.py
│   ├── security.py
│   ├── dependencies.py
│   ├── email_service.py
│   └── config/
│
├── users/
│   ├── users_model.py
│   ├── users_route.py
│   ├── users_service.py
│   └── users_schemas.py
│
├── inventory/
│   ├── inventory_model.py
│   ├── inventory_route.py
│   ├── inventory_service.py
│   └── inventory_schema.py
│
├── financery/
│   ├── financery_models.py
│   ├── financery_route.py
│   ├── financery_services.py
│   └── financery_schema.py

├── contacts/
│   ├── contacts_model.py
│   ├── contacts_route.py
│   └── contacts_service.py
│
├── frontend/
│   ├── templates/
│   └── static/
│
├── alembic/
│   └── versions/
│
├── .gitignore
├── README.md
├── alembic.ini
├── config_example.yaml
└── requirements.txt
```

## 🚀 Instalación

- Primero clonas el repositorio en tu maquina

```bash
git clone https://github.com/Toulousegg/erm.git
```
- Creas un entorno virtual para poder trabajar comodamente y lo activas

```bash
#crear entorno virtual
python -m venv venv

#activarlo
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

- instalas las dependencias del sistema
```bash
pip install -r requirements.txt
```

- rellenas los campos del archivo "config_example.yaml" con informacion coherente (#)

- Ejecutan el proyecto y abren en el navegador
```bash
#ejecutar el proyecto
uvicorn core.main:app --reload

#CTRL + Click Derecho en
http://127.0.0.1:8000
```

## 📌 Funcionalidades
✔️ Autenticación de usuarios

✔️ Inventario

✔️ Contactos

👨🏻‍💻 Financiero (En proceso)

👨🏻‍💻 Agente de IA (En proceso)

✔️ Gestión de empresas

✔️ WebSockets para notificaciones

❌ Exportación de reportes (pendiente)

❌ Compartir links para dar seguimiento a los proyectos con el cliente final (pendiente)

## 🤝 Contribución

Todos son bienvenidos a ayudar y poner su granito de arena en este sistema y futuro SaaS

***Para hacerlo siga estos pasos:***

1. Haz un **fork** del repositorio  
2. Crea una nueva rama:*

```bash
#cambia y guarda
> git checkout -b feature/nueva-funcionalidad

#añade los cambios
> git add

#haz commit
> git commit -m 'nueva_funcionalidad'

#sube la rama
> git push origin feature/nueva-funcionalidad

#ve a GitHub y haz Pull Request
```

## 📏 Estándares del Proyecto

Este proyecto sigue una estructura modular estricta para mantener escalabilidad, orden y mantenibilidad.

---

## 🧱 Estructura modular obligatoria

Cada nueva funcionalidad debe crearse como un **módulo independiente** dentro de `modules/`.

### 📌 Regla principal:
> Una carpeta por cada parte específica del sistema.

Ejemplo:
```
modules/
├── users/
├── inventory/
├── financery/
├── contacts/
└── new_feature/
```

---

## 📁 Estructura obligatoria de cada módulo

Cada módulo debe seguir este patrón:
```
new_module/
├── model.py
├── service.py
├── route.py
└── schema.py
```

---

## 🧠 Reglas importantes

- ✔️ No mezclar lógica entre módulos
- ✔️ Cada módulo debe ser independiente
- ✔️ No importar lógica interna de otros módulos directamente
- ✔️ Toda comunicación debe pasar por servicios (`service.py`)
- ✔️ Los endpoints siempre van en `route.py`
- ✔️ Validaciones siempre en `schema.py`

---

## 🏷️ Convención de nombres

Se debe respetar el estilo ya existente:

- `users_model.py`
- `inventory_service.py`
- `contacts_route.py`

Para nuevos módulos dentro de `modules/`:

- `model.py`
- `service.py`
- `route.py`
- `schema.py`

---

## 💬 Convención de commits

Se debe seguir el estándar:

### Tipos permitidos:

- `feat:` nueva funcionalidad
- `fix:` corrección de bugs
- `refactor:` mejoras de código sin cambiar lógica
- `docs:` cambios en documentación
- `test:` pruebas
- `chore:` mantenimiento general

### Ejemplos:

```bash
git commit -m "feat: add inventory stock validation"
git commit -m "fix: correct user authentication bug"
git commit -m "refactor: improve service layer structure"
```

#### #para pruebas, pueden eliminar las filas que guardan la informacion del email, pero si lo quieren llenar y ver todas las funcionalidades del sistema pueden acceder a esa informacion directamente desde su aplicacion de correo electronico

#### *Por favor, siempre crear rama desde main, desarrollar el modulo deseado siguiendo la estructura obligatoria, agradezco la comprensión de todos