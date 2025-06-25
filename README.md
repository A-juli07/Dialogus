# **Dialogus - Sistema de Chat com WebSockets**

**Dialogus** é um sistema de chat em tempo real com suporte a **mensagens diretas (DM)**, **salas públicas e privadas**, **convites** e **perfil de usuário**. O sistema é construído com o Django e WebSockets para permitir comunicação em tempo real entre os usuários.

## **Funcionalidades**
- **Mensagens Diretas (DM)**: O usuário pode enviar mensagens privadas para outros usuários.
- **Salas de Chat**: Salas públicas e privadas podem ser criadas e gerenciadas.
- **Convites**: Envio de convites para usuários entrarem em salas privadas ou conversas diretas.
- **Perfil de Usuário**: O usuário pode visualizar e editar seu perfil (foto, status e biografia).
- **WebSockets**: Utiliza **WebSockets** para comunicação em tempo real entre os usuários.

## **Tecnologias Utilizadas**
- **Django**: Framework Python para desenvolvimento web.
- **Channels**: Extensão do Django para suportar WebSockets.
- **Bootstrap**: Framework CSS para criação de interfaces responsivas.
- **SQLite**: Banco de dados para armazenamento de dados (pode ser alterado para outros como PostgreSQL).

## **Pré-Requisitos**
- **Python 3.8+**: Certifique-se de ter o Python instalado no seu ambiente.
- **Django 3.0+**: Framework web utilizado para o backend.
- **Channels**: Para suporte a WebSockets.
- **Redis**: Necessário para o layer de canais do Django Channels (pode ser substituído por outro backend de canal).
### 1. **Clonar o Repositório**
Clone o repositório do projeto para a sua máquina local:

```bash
git clone https://github.com/seu-usuario/dialogus.git 
```
### 2. Criar um Ambiente Virtual
Crie um ambiente virtual para isolar as dependências do projeto:

```bash
cd dialogus
python -m venv venv
```
### 3. Ativar o Ambiente Virtual
Ative o ambiente virtual.

Windows:
```bash
.\venv\Scripts\activate
```
Mac/Linux:
```bash
source venv/bin/activate
```
### 4. Instalar as Dependências
Com o ambiente virtual ativado, instale as dependências do projeto:

```bash
pip install -r requirements.txt
As dependências incluem Django, Channels, Redis, entre outras.
```
### 5. Configurar o Redis
O Django Channels usa Redis para a camada de canais WebSocket. Certifique-se de ter o Redis instalado e em execução. Você pode seguir o guia de instalação do Redis para o seu sistema operacional.

Iniciar o Redis:

```bash
redis-server
```
### 6. Configurar o Banco de Dados
Execute as migrações para configurar o banco de dados (utilizando SQLite, por padrão):

```bash
python manage.py migrate
```
### 7. Criar um Superusuário (Opcional)
Se desejar acessar o painel de administração do Django, crie um superusuário:
```bash
python manage.py createsuperuser
```
### 8. Rodar o Servidor Localmente
Inicie o servidor de desenvolvimento do Django para rodar o projeto localmente:
```bash
python manage.py runserver
```
O projeto estará acessível no endereço http://127.0.0.1:8000.

### 9. Testar o WebSocket
Para testar as funcionalidades de chat em tempo real, você precisará abrir múltiplas abas no navegador e se conectar ao WebSocket. O WebSocket será automaticamente gerenciado pelo Django Channels.

### 10. Acessar a Interface do Admin (Opcional)
Você pode acessar o painel de administração do Django, se desejar, indo para http://127.0.0.1:8000/admin.

Use o superusuário criado anteriormente para fazer login.

## Funções do Sistema
- Registrar novo usuário: O sistema permite que novos usuários se registrem e criem uma conta.
- Login e Logout: Usuários podem se logar e se deslogar facilmente.
- Mensagens Diretas: Envio de mensagens privadas entre dois usuários (sem a necessidade de um grupo de chat).
- Salas Públicas e Privadas: Usuários podem entrar em salas públicas e privadas ou criar novas.
- Convites: Usuários podem enviar convites para outros entrarem em salas privadas ou iniciar conversas de DM.
- Perfil de Usuário: A tela de perfil permite que o usuário edite a foto de perfil, status e biografia.

## Estrutura do Projeto

- chat/: O aplicativo principal que contém as funcionalidades de chat, como envio de mensagens e gerenciamento de salas.
- models.py: Definição de modelos para salas, mensagens e perfis.
- views.py: Lógica das páginas de chat e perfil.
- urls.py: Definição das URLs do sistema.
- templates/: Contém os templates HTML das páginas.
- settings.py: Arquivo de configuração do Django, onde você pode ajustar os detalhes do banco de dados, canais, e outras configurações.
- urls.py: Arquivo onde as URLs do projeto são definidas.
