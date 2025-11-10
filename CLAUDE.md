# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Dialogus** is a real-time chat application built with Django 5.2.1 and Django Channels 4.0.0. It provides direct messaging (DM), public/private group chat rooms, user invitations, and profile management. The entire codebase is written in Portuguese (pt-br).

**Key Technologies:**
- Backend: Django with async WebSocket support via Django Channels
- Message Broker: Redis (required for WebSocket channel layer)
- Database: SQLite (development), should use PostgreSQL in production
- Frontend: Bootstrap 5.3.0 with vanilla JavaScript
- Server: Daphne (ASGI server for WebSocket support)

## Development Commands

### Initial Setup
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Start Redis (required for WebSockets)
redis-server

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### Running the Application
```bash
# Start development server (supports WebSockets)
daphne -p 8000 chatproject.asgi:application

# Alternative: Django dev server (HTTP only, no WebSocket support)
python manage.py runserver
```

### Database Operations
```bash
# Create new migration after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access Django shell
python manage.py shell
```

### Testing
No test suite currently exists. To add tests:
```bash
# Run tests (once created)
python manage.py test

# Run specific test
python manage.py test chat.tests.TestClassName
```

## Architecture

### Project Structure
```
Dialogus/
├── chatproject/          # Django project configuration
│   ├── settings.py       # Main settings (IMPORTANT: has hardcoded SECRET_KEY for dev only)
│   ├── urls.py           # Root URL routing
│   └── asgi.py           # ASGI config with WebSocket routing
├── chat/                 # Main application
│   ├── models.py         # Core models: Sala, Mensagem, SalaPrivada, MensagemDM, Amizade, Perfil
│   ├── views.py          # HTTP request handlers
│   ├── consumers.py      # WebSocket handlers: ChatConsumer, NotificationConsumer
│   ├── forms.py          # Form definitions
│   └── urls.py           # App-level URL routing
├── templates/            # HTML templates (Portuguese language)
│   └── chat/
├── media/perfil/         # User-uploaded profile pictures
└── db.sqlite3            # SQLite database
```

### Core Models

**Sala (Group Room):**
- Represents both public and private chat groups
- `is_dm=True` flag used for direct messages (though SalaPrivada is preferred for DMs)
- Private rooms require password authentication stored in session: `sala_{id}_autorizado`
- UUID-based invite token system for private room access

**SalaPrivada (DM Room):**
- Handles one-to-one direct messaging
- Unique room per user pair with naming convention: `{min_user_id}_{max_user_id}`
- Requires friendship invitation/acceptance via Amizade model

**Amizade (Friendship/Invitation):**
- Manages DM invitation system
- Tracks invitation status (pending/accepted)

**Perfil (User Profile):**
- One-to-one relationship with Django User
- Auto-created on first access using `get_or_create()`

**Mensagem & MensagemDM:**
- Store chat history for groups and DMs respectively
- MensagemDM includes `lida` (read) flag for notification tracking

### WebSocket Architecture

**Real-time communication uses Django Channels with two WebSocket routes:**

1. **ChatConsumer** (`ws/chat/<room_name>/`):
   - Handles all chat messages (both groups and DMs)
   - Room group naming: `chat_{sanitized_room_name}`
   - Saves messages to database using `sync_to_async`
   - Broadcasts messages to all connected clients in the room
   - Sends notifications to DM recipients via NotificationConsumer

2. **NotificationConsumer** (`ws/notifications/<user_id>/`):
   - User-specific notification channel
   - Group naming: `user_{user_id}`
   - Updates unread message badge counts in real-time

**Important:** Redis must be running on localhost:6379 for WebSockets to work. The channel layer configuration is in [chatproject/settings.py](chatproject/settings.py).

**WebSocket Message Flow:**
```
1. User sends message → Frontend WebSocket (room.html)
2. ChatConsumer.receive() gets JSON message
3. Save to database (Mensagem or MensagemDM) via sync_to_async
4. If DM: Send notification to recipient's NotificationConsumer group
5. Broadcast message to all clients in chat room group
6. Frontend receives message → Updates chat UI
```

### URL Patterns

**Main routes:**
- `/` - Index (dashboard with DMs and invitations)
- `/register/` - User registration
- `/accounts/login/` - Django auth login
- `/chat/salas/` - Browse public/private rooms
- `/chat/criar-sala/` - Create new group room
- `/chat/chat/<room_name>/` - Chat room view (handles both DM and group)
- `/chat/dm/<user_id>/` - Create/access DM with specific user
- `/chat/perfil/` - User profile editor
- `/admin/` - Django admin panel

### Authentication & Authorization

- Django's built-in session-based auth
- All chat views require `@login_required` decorator
- Private room authorization stored in session after password verification
- WebSocket authentication via `AuthMiddlewareStack` in [chatproject/asgi.py](chatproject/asgi.py)
- DM access controlled by Amizade model (invitation must be accepted)

### Key View Functions

**`room(request, room_name)`** - Most complex view, handles both DM and group chats:
- Detects DM by checking if `_` is in `room_name`
- For DMs: Retrieves `SalaPrivada` and `MensagemDM`, marks messages as read
- For groups: Checks authorization (public/owner/session-based password auth)
- Loads last 50 messages for display
- Returns different context based on room type

**`aceitar_convite_dm(request, convite_id)`** - DM invitation acceptance:
- Sets `Amizade.aceita = True`
- Creates `SalaPrivada` room with sorted user IDs
- Critical for establishing DM capability between users

**`sala_privada_dm(request, user_id)`** - DM initiation:
- Redirects to existing DM or shows invitation form
- Uses consistent room naming pattern

### Frontend Architecture

- Bootstrap 5.3.0 for responsive UI
- Vanilla JavaScript (no framework)
- WebSocket connections established in templates with hardcoded `ws://` protocol
- Base template: [templates/chat/base.html](templates/chat/base.html) with collapsible sidebar
- All UI text in Portuguese

## Important Implementation Details

### Critical: DM vs Group Room Architecture
The codebase uses TWO different approaches for DM rooms, which can be confusing:

1. **SalaPrivada Model (Preferred):**
   - Dedicated model for DMs with `usuario1` and `usuario2` fields
   - Messages stored in `MensagemDM` table
   - Requires `Amizade` (friendship) acceptance
   - Room name pattern: `{min_user_id}_{max_user_id}`

2. **Sala Model with is_dm=True (Deprecated):**
   - Some views still create `Sala` objects with `is_dm=True` flag
   - This is inconsistent with the SalaPrivada approach
   - Should be refactored to use SalaPrivada exclusively

**The presence of underscore `_` in room name is the universal identifier for DM detection across the codebase.** This pattern is used in both `ChatConsumer` and view functions to branch logic between DM and group chat handling.

### Room Name Sanitization & DM Detection Pattern
DM rooms use the pattern `{min_user_id}_{max_user_id}` to ensure consistent room naming. This pattern is CRITICAL because it's used throughout the codebase to detect if a room is a DM:

```python
# In views.py - Creating DM room
id1, id2 = sorted([user1.id, user2.id])
room_name = f"{id1}_{id2}"

# In consumers.py - Detecting DM by presence of underscore
if '_' in nome_sala:  # This is a DM
    # Handle DM logic
else:  # This is a group room
    # Handle group logic
```

The underscore presence is the key identifier used in both `ChatConsumer.salvar_mensagem()` and `views.room()` to branch between DM and group chat logic.

### Message Saving Pattern
In ChatConsumer, use `sync_to_async` decorator when saving messages to avoid blocking the async event loop:
```python
@sync_to_async
def salvar_mensagem(self, usuario, nome_sala, conteudo):
    # Database operations here

# Call with await
await self.salvar_mensagem(user, room_name, message)
```

### Session-Based Authorization
Private rooms store authorization in session after password verification:
```python
request.session[f'sala_{sala.id}_autorizado'] = True
```
Check this session key before allowing room access.

### Notification System
When sending DM messages, the ChatConsumer checks if the room is a DM (by name pattern with `_`) and sends notifications to the recipient's notification channel:

```python
# In ChatConsumer.receive() after saving message
if destinatario_id:  # This is a DM
    await self.channel_layer.group_send(
        f"user_{destinatario_id}",
        {
            'type': 'nova_dm',
            'sala_id': sala_id,
            'from_user': user.username,
        }
    )
```

The index page connects to the NotificationConsumer WebSocket to update unread badges in real-time. The badge updates happen client-side via JavaScript incrementing the counter.

### Profile Auto-Creation
User profiles are created lazily when first accessed using:
```python
perfil, created = Perfil.objects.get_or_create(usuario=request.user)
```

### Unread Message System
The unread message tracking system works across multiple components:

**Backend (views.py - index view):**
```python
# Count unread messages for each DM
unread_count = MensagemDM.objects.filter(
    sala_dm=dm,
    lida=False
).exclude(usuario=request.user).count()
```

**Backend (views.py - room view):**
```python
# Mark messages as read when viewing DM
MensagemDM.objects.filter(
    sala_dm=sala_dm,
    lida=False
).exclude(usuario=request.user).update(lida=True)
```

**Real-time updates (WebSocket):**
- ChatConsumer sends notification to recipient's NotificationConsumer
- Frontend JavaScript increments badge counter dynamically
- Badge display controlled by `style.display` property

## Development Notes

### Language
All code, comments, variables, and UI text are in Portuguese. Key terms:
- Sala = Room/Group
- Mensagem = Message
- Usuário = User
- Amizade = Friendship
- Perfil = Profile
- Convite = Invitation
- Privada = Private

### Database Migrations
Currently on 11 migrations. When modifying models:
1. Always run `makemigrations` after model changes
2. Review the generated migration before applying
3. The SalaPrivada model has a unique_together constraint on (usuario1, usuario2)

### WebSocket Protocol
Frontend uses hardcoded `ws://` protocol. For HTTPS deployments, this must be changed to `wss://` or made dynamic based on page protocol.

### Security Considerations for Production
**Critical Issues:**
- `SECRET_KEY` is hardcoded in settings.py - MUST use environment variables in production
- `DEBUG = True` - MUST be False in production
- `ALLOWED_HOSTS = []` - MUST be configured for production
- SQLite database - Should use PostgreSQL in production
- **Private room passwords stored in plaintext** in `Sala.senha` field (should use Django's `make_password()`)
- WebSocket protocol hardcoded as `ws://` in templates (won't work with HTTPS)
- No rate limiting implemented
- No input sanitization beyond Django's default CSRF protection

### Missing Components
- No test suite exists
- No admin.py registration for models (admin panel won't show chat models)
- Django REST Framework is installed but unused (no API endpoints)
- No logging configuration
- No static files directory (using CDN links)
- __pycache__ files tracked in git (should be in .gitignore)

## Common Workflows

### Adding a New Chat Feature
1. Update models in [chat/models.py](chat/models.py) if database changes needed
2. Run `makemigrations` and `migrate`
3. Add view logic in [chat/views.py](chat/views.py)
4. Update URL patterns in [chat/urls.py](chat/urls.py)
5. Create/update templates in [templates/chat/](templates/chat/)
6. If real-time updates needed, modify consumers in [chat/consumers.py](chat/consumers.py)

### Debugging WebSocket Issues
1. Ensure Redis is running: `redis-server` on port 6379
2. Check browser console for WebSocket connection errors (look for `ws://` connection status)
3. Verify ASGI routing in [chatproject/asgi.py](chatproject/asgi.py)
4. Check channel layer config in [chatproject/settings.py](chatproject/settings.py)
5. Use `print()` statements in consumers (appears in Daphne console output)
6. Test Redis connection: `redis-cli ping` should return `PONG`
7. Check that user is authenticated in consumer: `print(self.scope["user"].is_authenticated)`
8. Verify room group name sanitization - special characters are replaced with underscores

### Creating a New Room Type
1. Add fields to Sala model or create new model like SalaPrivada
2. Update room creation view to handle new type
3. Modify ChatConsumer to handle routing if different WebSocket logic needed
4. Update room listing views to display new type

## Production Deployment Checklist

- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure environment variables for secrets (SECRET_KEY, database credentials)
- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS
- [ ] Change WebSocket protocol to wss:// for HTTPS (or make dynamic based on page protocol)
- [ ] Configure Redis for production (password, persistence)
- [ ] Set up static file serving (collectstatic + nginx/CDN)
- [ ] Configure HTTPS/TLS certificates
- [ ] Use Gunicorn for HTTP + Daphne for WebSocket (or use Daphne for both)
- [ ] Add logging configuration
- [ ] Implement rate limiting
- [ ] Add input validation and sanitization
- [ ] Remove __pycache__ from git tracking (add to .gitignore)
- [ ] Hash private room passwords using Django's `make_password()`
- [ ] Set up monitoring and error tracking
- [ ] Configure proper CORS settings if needed
- [ ] Set up Redis password authentication

## Quick Reference

### Checking if a Room is a DM
```python
is_dm = '_' in room_name  # True if DM, False if group
```

### Getting or Creating a DM Room
```python
u1, u2 = sorted([user1, user2], key=lambda u: u.id)
sala_dm, created = SalaPrivada.objects.get_or_create(usuario1=u1, usuario2=u2)
room_name = sala_dm.get_nome_sala()  # Returns "{min_id}_{max_id}"
```

### Sending WebSocket Message from Frontend
```javascript
chatSocket.send(JSON.stringify({
    'message': messageText
}));
```

### Broadcasting to a Channel Group (in Consumer)
```python
await self.channel_layer.group_send(
    self.room_group_name,
    {
        'type': 'chat_message',  # Maps to chat_message() method
        'message': message,
        'username': username
    }
)
```

### Checking Session-Based Room Authorization
```python
autorizado = request.session.get(f'sala_{sala.id}_autorizado', False)
```
