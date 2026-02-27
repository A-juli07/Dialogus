# Dialogus

Sistema de chat em tempo real com suporte a mensagens diretas, salas públicas e privadas, convites e perfis de usuário.

## Funcionalidades

- **Mensagens diretas (DM)** — conversas privadas entre dois usuários
- **Salas de grupo** — públicas ou privadas, com senha ou convite por link
- **Notificações em tempo real** — badge de mensagens não lidas atualizado via WebSocket
- **Perfil de usuário** — foto, status e biografia editáveis
- **Busca** — pesquisa dentro de conversas e na lista de contatos

## Stack

- **Django + Django Channels** — backend e WebSockets
- **Daphne** — servidor ASGI (necessário para WebSocket)
- **Redis** — canal de mensagens para os WebSockets
- **SQLite** — banco de dados padrão

---

## Como rodar

### Docker (recomendado)

Requer [Docker](https://www.docker.com/get-started) instalado.

```bash
git clone https://github.com/seu-usuario/dialogus.git
cd dialogus
docker-compose up --build
```

Acesse em **http://localhost:8000**

O Docker sobe automaticamente o Redis, o Daphne e aplica as migrações. Cria também um superusuário padrão:
- Usuário: `admin`
- Senha: `admin123`

Comandos úteis:

```bash
docker-compose up -d          # rodar em background
docker-compose logs -f        # ver logs em tempo real
docker-compose down           # parar os serviços
docker-compose down -v        # parar e apagar o banco de dados
docker-compose up --build     # reconstruir após mudanças
```

---

### Manual

**Pré-requisitos:** Python 3.8+, Redis rodando em `localhost:6379`

```bash
git clone https://github.com/seu-usuario/dialogus.git
cd dialogus

# Criar e ativar ambiente virtual
python -m venv venv
.\venv\Scripts\activate        # Windows
source venv/bin/activate       # Mac/Linux

# Instalar dependências
pip install -r requirements.txt

# Banco de dados
python manage.py migrate
python manage.py createsuperuser   # opcional

# Iniciar o servidor
daphne -p 8000 chatproject.asgi:application
```

Acesse em **http://127.0.0.1:8000**

> **Atenção:** use `daphne`, não `python manage.py runserver`. O runserver padrão do Django não suporta WebSockets.

---

## Painel admin

Disponível em `/admin` com as credenciais do superusuário criado.
