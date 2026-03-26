ERM (Enterprise Resource Management)

































































Descripción

ERM es un sistema de gestión de recursos empresariales diseñado para optimizar la administración de inventario, contactos y finanzas. Desarrollado con FastAPI para un rendimiento robusto y PostgreSQL como base de datos principal, este proyecto implementa una arquitectura escalable y segura, incluyendo autenticación basada en JWT (JSON Web Tokens). El objetivo es proporcionar una solución integral para la gestión interna de una empresa, mejorando la comunicación con clientes y proveedores, y reduciendo los tiempos de búsqueda de material.

Características

•
Gestión de Inventario: Control de entradas, salidas y estado de materiales.

•
Gestión de Contactos: Administración de clientes y proveedores.

•
Gestión Financiera: Módulos para el seguimiento de transacciones y modelos financieros.

•
Autenticación Segura: Implementación de JWT y Bcrypt para la gestión de usuarios y roles.

•
API RESTful: Interfaz robusta para la interacción con el frontend y otros servicios.

•
Persistencia de Datos: Uso de PostgreSQL con SQLAlchemy para un ORM eficiente y Alembic para migraciones de base de datos.

•
Frontend Básico: Interfaz funcional desarrollada con Jinja2, HTML5 y CSS3 para el registro y visualización de datos.

Tecnologías Utilizadas

•
Backend: Python 3.11+, FastAPI, Spring Boot (mencionado en CV, pero el repo es Python), Uvicorn

•
Bases de Datos: PostgreSQL, SQLite

•
ORM/Migraciones: SQLAlchemy, Alembic

•
Seguridad: OAuth2, JWT (python-jose), Bcrypt

•
Frontend: Jinja2, HTML5, CSS3

•
Herramientas: Git, Docker, Pydantic, Python-dotenv

Arquitectura

El proyecto sigue una arquitectura modular, separando las responsabilidades en diferentes componentes (usuarios, inventario, contactos, finanzas). Se utiliza un enfoque de API RESTful para la comunicación entre el frontend y el backend. La persistencia de datos se maneja a través de SQLAlchemy y Alembic, asegurando un esquema de base de datos versionado y robusto.

(Aquí podrías añadir un diagrama de arquitectura si lo tienes, por ejemplo, un diagrama de componentes o de base de datos.)

Instalación y Configuración

Sigue estos pasos para configurar y ejecutar el proyecto localmente:

Prerrequisitos

•
Python 3.11+

•
Docker (opcional, para PostgreSQL)

•
pip (administrador de paquetes de Python)

1. Clonar el Repositorio

Bash


git clone https://github.com/Toulousegg/erm.git
cd erm



2. Configurar el Entorno Virtual

Es crucial crear un entorno virtual para gestionar las dependencias del proyecto.

Bash


python3.11 -m venv venv
source venv/bin/activate  # En Linux/macOS
# venv\Scripts\activate  # En Windows



3. Instalar Dependencias

Bash


pip install -r requirements.txt



(Asegúrate de tener un archivo requirements.txt actualizado en tu repositorio. )

4. Configuración de Variables de Entorno

Crea un archivo .env en la raíz del proyecto basado en config_example.yaml (o un .env.example si prefieres) y configura las variables necesarias, como las credenciales de la base de datos y la clave secreta para JWT.

Plain Text


# .env
DATABASE_URL="postgresql://user:password@host:port/database_name"
SECRET_KEY="tu_super_clave_secreta_aqui"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30



5. Configurar y Ejecutar PostgreSQL (con Docker, recomendado)

Si no tienes PostgreSQL instalado, puedes usar Docker:

Bash


docker-compose up -d postgres



(Asegúrate de tener un docker-compose.yml para PostgreSQL en tu repositorio.)

6. Ejecutar Migraciones de Base de Datos

Bash


alembic upgrade head



7. Iniciar el Servidor FastAPI

Bash


uvicorn main:app --reload



El servidor estará disponible en http://127.0.0.1:8000.

Uso de la API

La API está documentada automáticamente con Swagger UI (OpenAPI ) y ReDoc, accesibles en:

•
Swagger UI: http://127.0.0.1:8000/docs

•
ReDoc: http://127.0.0.1:8000/redoc

Utiliza estas interfaces para explorar los endpoints disponibles, probar las solicitudes y entender la estructura de la API.

Contribución

Las contribuciones son bienvenidas. Por favor, sigue los siguientes pasos:

1.
Haz un fork del repositorio.

2.
Crea una nueva rama (git checkout -b feature/nueva-funcionalidad ).

3.
Realiza tus cambios y asegúrate de que las pruebas pasen.

4.
Escribe mensajes de commit claros y descriptivos (siguiendo Conventional Commits).

5.
Envía un Pull Request.

Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

