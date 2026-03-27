[🇺🇸 English](#english) | [🇪🇸 Español](#español) | [🇧🇷 Português](#português)

<a name="español"></a>
================================================================
                ESPAÑOL (ORIGINAL)
================================================================
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
erm/
├── users/
├── inventory/
├── financery/
├── contacts/
└── new_module/
```

---

## 📁 Estructura obligatoria de cada módulo

Cada módulo debe seguir este patrón:
```
new_module/
├── %_model.py
├── %_service.py
├── %_route.py
└── %_schema.py
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
<<<<<<< HEAD

<a name="english"></a>
================================================================
                ENGLISH
================================================================
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

This multi-tenancy ERP system aims to solve common problems for factories and distributors of loose and custom-made furniture. It features inventory control, factory production management, projects separated by environment and/or client, and the ability to share a link so clients can track their orders in real-time, offering total transparency to both clients and architects. It also assists in tracking company finances with various charts and tables to analyze income/expenses/profits organized by type. All this is supported by an AI agent using the Gemini engine to perform tasks and assist users with their questions. The application includes a WebSocket system for real-time notifications, ensuring all users stay informed about decisions and activities within their workspace.

---

## 📸 Preview

![Home](https://i.imgur.com/Z89LSHn.png)

![Login](https://i.imgur.com/Z8B7FX5.png)

![Signup](https://i.imgur.com/SBVbcZB.png)

![Inventory](https://i.imgur.com/h0xzs4F.png)

![Verify Email](https://i.imgur.com/hvAY55S.png)

![Notifications](https://i.imgur.com/lZjmEA6.png)

---

## 🧠 Description

This project aims to solve:

This system allows small and medium-sized carpenter shops and furniture businesses to manage stock, contacts, production, finances, and projects in one place, reducing human errors, improving traceability and communication, and giving carpenters the opportunity to focus more on their work without wasting time or energy on logistics and bureaucracy by maintaining client contact in a easier and more satisfactory way for the user.



## ⚙️ Technologies Used

#### Backend & API
+ FastAPI
+ Uvicorn
+ Starlette

#### Database & ORM
+ SQLAlchemy
+ Alembic
+ PostgreSQL (psycopg2)

#### Security & Authentication
+ JWT (python-jose)
+ Passlib (Bcrypt)
+ Cryptography

#### Validation & Configuration
+ Pydantic
+ Pydantic-Settings
+ Python-dotenv

#### Communication & Utilities
+ FastAPI-Mail (aiosmtplib)
+ Jinja2
+ AnyIO
+ Websockes
---

## 🏗️ Project Structure
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

## 🚀 Installation

- First, clone the repository to your machine

```bash
git clone https://github.com/Toulousegg/erm.git
```
- Create a virtual environment to work comfortably and activate it

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

- Install system dependencies
```bash
pip install -r requirements.txt
```

- Fill in the fields in the "config_example.yaml" file with consistent information (#)

- Run the project and open it in your browser
```bash
# Run the project
uvicorn core.main:app --reload

# CTRL + Right Click on
http://127.0.0.1:8000
```

## 📌 Features
✔️ User Authentication

✔️ Inventory

✔️ Contacts

👨🏻‍💻 Financial (In progress)

👨🏻‍💻 AI Agent (In progress)

✔️ Company Management

✔️ WebSockets for notifications

❌ Report Export (Pending)

❌ Share links to track projects with the end client (Pending)

## 🤝 Contribution

Everyone is welcome to help and contribute to this system and future SaaS.

***To do so, follow these steps:***

1. **Fork** the repository  
2. Create a new branch:

```bash
# Switch and save
> git checkout -b feature/new-feature

# Add changes
> git add .

# Commit
> git commit -m 'new_feature'

# Push the branch
> git push origin feature/new-feature

# Go to GitHub and create a Pull Request
```

## 📏 Project Standards

This project follows a strict modular structure to maintain scalability, order, and maintainability.

---

## 🧱 Mandatory Modular Structure

Each new feature must be created as an **independent module** inside `modules/`.

### 📌 Main Rule:
> One folder for each specific part of the system.

Example:
```
erm/
├── users/
├── inventory/
├── financery/
├── contacts/
└── new_module/
```

---

## 📁 Mandatory Structure for Each Module

Each module must follow this pattern:
```
new_module/
├── %_model.py
├── %_service.py
├── %_route.py
└── %_schema.py
```

---

## 🧠 Important Rules

- ✔️ Do not mix logic between modules
- ✔️ Each module must be independent
- ✔️ Do not import internal logic from other modules directly
- ✔️ All communication must go through services (`service.py`)
- ✔️ Endpoints always go in `route.py`
- ✔️ Validations always in `schema.py`

---

## 🏷️ Naming Convention

The existing style must be respected:

- `users_model.py`
- `inventory_service.py`
- `contacts_route.py`

For new modules inside `modules/`:

- `model.py`
- `service.py`
- `route.py`
- `schema.py`

---

## 💬 Commit Convention

The standard must be followed:

### Allowed Types:

- `feat:` new feature
- `fix:` bug fix
- `refactor:` code improvements without changing logic
- `docs:` documentation changes
- `test:` tests
- `chore:` general maintenance

### Examples:

```bash
git commit -m "feat: add inventory stock validation"
git commit -m "fix: correct user authentication bug"
git commit -m "refactor: improve service layer structure"
```

#### # For testing, you can remove the rows that save email information, but if you want to fill them and see all system features, you can access that information directly from your email application.

#### * Please always create branches from main, develop the desired module following the mandatory structure, thank you for your understanding.

<a name="português"></a>
================================================================
                PORTUGUÊS
================================================================
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

Este sistema ERP multi-tenancy busca solucionar problemas comuns de fábricas e distribuidoras de móveis avulsos e sob medida. Possui controle de estoque, controle de produção na fábrica, projetos separados por ambiente e/ou cliente, com a possibilidade de compartilhar um link para que o cliente possa acompanhar seu pedido em tempo real, oferecendo total transparência ao cliente e arquitetos. Ajuda no acompanhamento das finanças da empresa, onde é possível visualizar diversos gráficos e tabelas para analisar as receitas/despesas/lucros de uma empresa e organizá-los por tipo. Tudo isso com a ajuda de um agente de IA que utiliza o motor do Gemini para executar tarefas e auxiliar os usuários com suas dúvidas. A aplicação conta com um sistema WebSocket para exibir notificações em tempo real, garantindo que todos os usuários estejam por dentro das decisiones e atividades em seu trabalho.

---

## 📸 Pré-visualização

![Home](https://i.imgur.com/Z89LSHn.png)

![Login](https://i.imgur.com/Z8B7FX5.png)

![Signup](https://i.imgur.com/SBVbcZB.png)

![Inventory](https://i.imgur.com/h0xzs4F.png)

![Verify Email](https://i.imgur.com/hvAY55S.png)

![Notifications](https://i.imgur.com/lZjmEA6.png)

---

## 🧠 Descrição

Este projeto busca resolver:

Este sistema permite que pequenas e médias marcenarias e negócios do setor moveleiro gerenciem estoque, contatos, produção, finanças e projetos em um só lugar, reduzindo erros humanos, melhorando a rastreabilidade e a comunicação, e dando a oportunidade aos marceneiros de se concentrarem mais em seu trabalho, sem perder tempo ou energia com logística e burocracias, mantendo o contato com o cliente de uma forma mais fácil e satisfatória para o usuário.



## ⚙️ Tecnologias Usadas

#### Backend & API
+ FastAPI
+ Uvicorn
+ Starlette

#### Banco de Dados & ORM
+ SQLAlchemy
+ Alembic
+ PostgreSQL (psycopg2)

#### Segurança & Autenticação
+ JWT (python-jose)
+ Passlib (Bcrypt)
+ Cryptography

#### Validação & Configuração
+ Pydantic
+ Pydantic-Settings
+ Python-dotenv

#### Comunicação & Utilidades
+ FastAPI-Mail (aiosmtplib)
+ Jinja2
+ AnyIO
+ Websockes
---

## 🏗️ Estrutura do Projeto
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

## 🚀 Instalação

- Primeiro, clone o repositório em sua máquina

```bash
git clone https://github.com/Toulousegg/erm.git
```
- Crie um ambiente virtual para trabalhar confortavelmente e ative-o

```bash
# Criar ambiente virtual
python -m venv venv

# Ativá-lo
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

- Instale as dependências do sistema
```bash
pip install -r requirements.txt
```

- Preencha os campos do arquivo "config_example.yaml" con informações coerentes (#)

- Execute o projeto e abra no navegador
```bash
# Executar o projeto
uvicorn core.main:app --reload

# CTRL + Clique Direito em
http://127.0.0.1:8000
```

## 📌 Funcionalidades
✔️ Autenticação de usuários

✔️ Inventário

✔️ Contatos

👨🏻‍💻 Financeiro (Em andamento)

👨🏻‍💻 Agente de IA (Em andamento)

✔️ Gestão de empresas

✔️ WebSockets para notificações

❌ Exportação de relatórios (Pendente)

❌ Compartilhar links para acompanhamento de projetos com o cliente final (Pendente)

## 🤝 Contribución

Todos são bem-vindos para ajudar e contribuir com este sistema e futuro SaaS.

***Para fazer isso, siga estes passos:***

1. Faça um **fork** del repositório  
2. Crie um novo branch:

```bash
# Muda e salva
> git checkout -b feature/nova-funcionalidade

# Adiciona as mudanças
> git add .

# Faz o commit
> git commit -m 'nova_funcionalidad'

# Sobe o branch
> git push origin feature/nova-funcionalidade

# Vá ao GitHub e faça o Pull Request
```

## 📏 Padrões do Projeto

Este proyecto segue uma estrutura modular estrita para manter escalabilidade, ordem e manutenibilidade.

---

## 🧱 Estrutura modular obrigatória

Cada nova funcionalidade deve ser criada como um **módulo independente** dentro de `modules/`.

### 📌 Regra Principal:
> Uma pasta para cada parte específica do sistema.

Exemplo:
```
erm/
├── users/
├── inventory/
├── financery/
├── contacts/
└── new_module/
```

---

## 📁 Estrutura obrigatória de cada módulo

Cada módulo deve seguir este padrão:
```
new_module/
├── %_model.py
├── %_service.py
├── %_route.py
└── %_schema.py
```

---

## 🧠 Regras importantes

- ✔️ Não misturar lógica entre módulos
- ✔️ Cada módulo deve ser independente
- ✔️ Não importar lógica interna de outros módulos diretamente
- ✔️ Toda comunicação deve passar por serviços (`service.py`)
- ✔️ Os endpoints sempre vão em `route.py`
- ✔️ Validações sempre em `schema.py`

---

## 🏷️ Convenção de nomes

O estilo já existente deve ser respeitado:

- `users_model.py`
- `inventory_service.py`
- `contacts_route.py`

Para novos módulos dentro de `modules/`:

- `model.py`
- `service.py`
- `route.py`
- `schema.py`

---

## 💬 Convenção de commits

O padrão deve ser seguido:

### Tipos permitidos:

- `feat:` nova funcionalidade
- `fix:` correção de bugs
- `refactor:` melhorias de código sem alterar a lógica
- `docs:` mudanças na documentação
- `test:` testes
- `chore:` manutenção geral

### Exemplos:

```bash
git commit -m "feat: add inventory stock validation"
git commit -m "fix: correct user authentication bug"
git commit -m "refactor: improve service layer structure"
```

#### # Para testes, você pode remover as linhas que salvam as informações de e-mail, mas se quiser preenchê-las e ver todas as funcionalidades do sistema, pode acessar essas informações diretamente do seu aplicativo de e-mail.

#### * Por favor, siempre crie branches a partir da main, desenvolva o módulo desejado seguindo a estrutura obrigatória, agradeço a compreensão de todos.
=======
>>>>>>> 2c3586ede064f2b825da4a84941e06ec7a925be3
