# 🐳 Docker - Guia de Uso do Dialogus

Este guia mostra como executar o projeto Dialogus usando Docker e Docker Compose.

## 📋 Pré-requisitos

- **Docker** instalado ([Download Docker](https://www.docker.com/get-started))
- **Docker Compose** instalado (geralmente vem com Docker Desktop)

## 🚀 Iniciando o Projeto

### 1. **Clone o repositório** (se ainda não fez)
```bash
git clone https://github.com/seu-usuario/dialogus.git
cd dialogus
```

### 2. **Construa e inicie os containers**

```bash
docker-compose up --build
```

Isso irá:
- 🐳 Baixar as imagens necessárias (Python, Redis)
- 📦 Instalar todas as dependências do Python
- 🗄️ Aplicar migrações do banco de dados automaticamente
- 👤 Criar um superusuário padrão (`admin` / `admin123`)
- 🚀 Iniciar o servidor Daphne (ASGI) na porta 8000
- 🔴 Iniciar o Redis na porta 6379

### 3. **Acesse a aplicação**

Abra seu navegador em: **http://localhost:8000**

### 4. **Acesse o painel admin**

URL: **http://localhost:8000/admin**
- **Usuário**: `admin`
- **Senha**: `admin123`

---

## 📝 Comandos Úteis

### Iniciar os containers (modo detached/background)
```bash
docker-compose up -d
```

### Ver logs em tempo real
```bash
docker-compose logs -f
```

### Ver logs apenas do serviço web
```bash
docker-compose logs -f web
```

### Parar os containers
```bash
docker-compose down
```

### Parar e remover volumes (apaga o banco de dados!)
```bash
docker-compose down -v
```

### Reconstruir as imagens após mudanças no código
```bash
docker-compose up --build
```

### Executar comandos Django dentro do container
```bash
# Exemplo: Criar migrações
docker-compose exec web python manage.py makemigrations

# Exemplo: Aplicar migrações
docker-compose exec web python manage.py migrate

# Exemplo: Criar superuser manualmente
docker-compose exec web python manage.py createsuperuser

# Exemplo: Coletar arquivos estáticos
docker-compose exec web python manage.py collectstatic
```

### Acessar o shell do Django
```bash
docker-compose exec web python manage.py shell
```

### Acessar o bash do container
```bash
docker-compose exec web bash
```

### Verificar status dos containers
```bash
docker-compose ps
```

---

## 🗂️ Estrutura dos Serviços

### **web** (Django + Daphne)
- Servidor ASGI rodando na porta `8000`
- Aplicação Django com suporte a WebSockets
- Volume montado para desenvolvimento em tempo real

### **redis**
- Servidor Redis rodando na porta `6379`
- Usado como backend para Django Channels (WebSockets)
- Dados persistidos em volume Docker

---

## 🔧 Configuração Avançada

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (use `.env.example` como base):

```bash
cp .env.example .env
```

Edite o arquivo `.env` conforme necessário:
```env
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_HOST=redis
REDIS_PORT=6379
```

### Usar PostgreSQL ao invés de SQLite

1. Adicione o serviço PostgreSQL no `docker-compose.yml`:
```yaml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_DB: dialogus
    POSTGRES_USER: dialogus_user
    POSTGRES_PASSWORD: dialogus_pass
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"
```

2. Atualize o `settings.py` para usar PostgreSQL
3. Adicione `psycopg2-binary` ao `requirements.txt`

---

## 🐛 Troubleshooting

### Erro "port already in use"
Se as portas 8000 ou 6379 já estiverem em uso:
```bash
# Encontrar processo usando a porta
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # Mac/Linux

# Ou altere as portas no docker-compose.yml
```

### Container não inicia
```bash
# Ver logs completos
docker-compose logs

# Reconstruir sem cache
docker-compose build --no-cache
docker-compose up
```

### Resetar completamente o ambiente
```bash
# Para tudo e remove volumes
docker-compose down -v

# Remove imagens antigas
docker-compose build --no-cache

# Inicia novamente
docker-compose up
```

---

## 📦 Volumes

Os seguintes volumes são criados para persistência de dados:

- **redis_data**: Dados do Redis
- **static_volume**: Arquivos estáticos do Django
- **media_volume**: Uploads de usuários (fotos de perfil)

Para fazer backup dos dados:
```bash
docker run --rm -v dialogus_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz -C /data .
```

---

## 🎯 Modo Produção

Para produção, recomenda-se:

1. Alterar `DEBUG=False` no `.env`
2. Usar uma `SECRET_KEY` forte e única
3. Configurar `ALLOWED_HOSTS` corretamente
4. Usar PostgreSQL ao invés de SQLite
5. Configurar um servidor Nginx como proxy reverso
6. Usar Docker secrets para senhas
7. Habilitar HTTPS

---

## 📚 Recursos Adicionais

- [Documentação do Docker](https://docs.docker.com/)
- [Documentação do Django](https://docs.djangoproject.com/)
- [Documentação do Django Channels](https://channels.readthedocs.io/)
- [Documentação do Daphne](https://github.com/django/daphne)

---

## 💡 Dicas

- **Desenvolvimento**: Use `docker-compose up` (sem `-d`) para ver logs em tempo real
- **Produção**: Use `docker-compose up -d` para rodar em background
- **Logs**: Sempre verifique os logs com `docker-compose logs -f` se algo der errado
- **Rebuild**: Após mudanças no `requirements.txt` ou `Dockerfile`, faça rebuild com `--build`

---

## 📞 Suporte

Se encontrar problemas, verifique:
1. Logs do Docker: `docker-compose logs`
2. Status dos containers: `docker-compose ps`
3. Versão do Docker: `docker --version` e `docker-compose --version`
