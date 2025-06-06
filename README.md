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
