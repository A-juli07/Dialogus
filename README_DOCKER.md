# 🚀 Iniciar o Projeto Dialogus

## Forma mais rápida (Docker) - Recomendado

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/dialogus.git
cd dialogus

# 2. Inicie todos os serviços
docker-compose up --build

# 3. Acesse a aplicação
# http://localhost:8000
```

**Credenciais padrão do admin:**
- Usuário: `admin`
- Senha: `admin123`

---

## 📦 O que o Docker faz automaticamente?

✅ Instala todas as dependências
✅ Configura o Redis
✅ Aplica migrações do banco de dados
✅ Cria um superusuário
✅ Inicia o servidor Daphne (ASGI)
✅ Tudo funcionando em 1 comando!

---

## 🛠️ Comandos Úteis

```bash
# Iniciar em background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar os serviços
docker-compose down

# Reconstruir após mudanças
docker-compose up --build
```

---

## 📚 Documentação Completa

- [DOCKER.md](DOCKER.md) - Guia completo do Docker
- [CLAUDE.md](CLAUDE.md) - Documentação para desenvolvedores
- [README.md](README.md) - Documentação original do projeto

---

## 🐛 Problemas?

Veja os logs:
```bash
docker-compose logs -f web
```

Reconstrua do zero:
```bash
docker-compose down -v
docker-compose up --build
```
