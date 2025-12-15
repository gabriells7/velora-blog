# Velora Blog

Um blog moderno e responsivo desenvolvido com **Django 5.2**, **PostgreSQL**, **Bootstrap 5** e **Chart.js**. Apresenta funcionalidades completas de gerenciamento de posts, comentários, categorias, tags e um sistema de notificações em tempo real.

## 🚀 Características

- ✅ Autenticação e registro de usuários com validação de email
- ✅ CRUD completo de posts (criar, editar, deletar, publicar)
- ✅ Sistema de categorias e tags
- ✅ Criação inline de categorias e tags via AJAX
- ✅ Comentários com moderação (aprovação automática)
- ✅ Sistema de notificações em tempo real
- ✅ Dashboard com estatísticas (posts, comentários, tendências de 6 meses)
- ✅ Interface moderna com Bootstrap 5 e Font Awesome 6
- ✅ Admin Django completo para gerenciamento
- ✅ Rascunhos de posts (não publicados)

## 📋 Requisitos

- **Python** 3.10+
- **pip** (gerenciador de pacotes Python)
- **PostgreSQL** 12+
- **virtualenv** (recomendado)
- (Opcional) **Docker** e **Docker Compose**

## 🔧 Configuração Local (Modo Manual)

### 1. Clone o repositório

```bash
git clone https://github.com/gabriells7/velora-blog.git
cd velora-blog
```

### 2. Crie e ative um ambiente virtual

**Linux / macOS:**

```bash
python3 -m venv myvenv
source myvenv/bin/activate
```

**Windows PowerShell:**

```powershell
python -m venv myvenv
.\myvenv\Scripts\Activate.ps1
```

**Windows CMD:**

```cmd
python -m venv myvenv
myvenv\Scripts\activate.bat
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o PostgreSQL

Abra o `psql` ou ferramentas PostgreSQL e execute:

```sql
CREATE DATABASE velora_blog;
CREATE USER velora_user WITH ENCRYPTED PASSWORD 'sua_senha_segura';
GRANT ALL PRIVILEGES ON DATABASE velora_blog TO velora_user;
```

### 5. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (mesmo nível do `manage.py`):

```env
# Database
DB_NAME=velora_blog
DB_USER=velora_user
DB_PASSWORD=sua_senha_segura
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=sua_chave_secreta_aqui
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_app
```

**Nota:** Para gerar uma `SECRET_KEY` segura, execute:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Aplique as migrações

```bash
python manage.py migrate
```

### 7. Colete os arquivos estáticos

```bash
python manage.py collectstatic --noinput
```

### 8. Crie um superusuário (admin)

```bash
python manage.py createsuperuser
```

Você será solicitado a informar:

- Username (ex: `admin`)
- Email (ex: `admin@example.com`)
- Password (será solicitado 2x)

### 9. Rode o servidor

```bash
python manage.py runserver
```

## 🌐 Acessos

Após executar o servidor, acesse:

- **Site Público:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin Django:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Dashboard:** [http://127.0.0.1:8000/usuario/](http://127.0.0.1:8000/usuario/) (requer login)
- **Notificações:** [http://127.0.0.1:8000/notificacoes/](http://127.0.0.1:8000/notificacoes/) (requer login)

## 📚 Estrutura do Projeto

```
velora-blog/
├── blog/                      # Aplicação principal Django
│   ├── models.py             # Modelos: Post, Comentário, Notificação, etc.
│   ├── views.py              # Views e lógica de negócio
│   ├── forms.py              # Formulários customizados
│   ├── urls.py               # Rotas da aplicação
│   ├── admin.py              # Configuração do admin Django
│   ├── context_processors.py # Processadores de contexto globais
│   └── migrations/           # Migrações do banco de dados
├── velora/                    # Configurações Django
│   ├── settings.py           # Variáveis e configurações
│   ├── urls.py               # Rotas principais
│   └── wsgi.py               # Configuração WSGI
├── templates/                # Templates HTML
│   ├── base.html             # Template base
│   ├── home.html             # Página inicial
│   ├── post_detail.html      # Detalhe do post
│   ├── new_post.html         # Criar/editar post
│   ├── notification.html     # Notificações
│   ├── dashboard.html        # Dashboard com estatísticas
│   └── ...                   # Outros templates
├── static/                   # Arquivos estáticos
│   ├── css/
│   │   └── style.css         # Estilos customizados
│   ├── js/
│   └── img/
├── media/                    # Upload de imagens
├── manage.py                 # Gerenciador Django
├── requirements.txt          # Dependências Python
└── README.md                 # Este arquivo
```

## 🗄️ Modelos Principais

### Post

- Título, slug, conteúdo, imagem de destaque
- Categorias (FK) e Tags (M2M)
- Autor, data de criação e publicação
- Status: rascunho ou publicado

### Comentário

- Associado a um post
- Autor, conteúdo
- Aprovação automática
- Timestamp

### Notificação

- Usuário destinatário
- Tipo (comentário novo, post publicado, etc.)
- Timestamp e status de leitura

### Categoria e Tag

- Nome e slug
- Relacionados a múltiplos posts

## 🔑 Funcionalidades Principais

### Autenticação

- Registro com validação de email (AJAX)
- Login com sessão Django
- Logout seguro

### Gerenciamento de Posts

- Criar posts como rascunho ou publicar imediatamente
- Slug gerado automaticamente do título
- Upload de imagem de destaque
- Data/hora pré-preenchida ao criar novo post

### Categorias e Tags

- Criação inline via AJAX ao criar/editar post
- Seleção de múltiplas tags
- Busca por categoria ou tag

### Comentários

- Formulário inline na página do post
- Aprovação automática
- Deletar comentários próprios
- Contagem em tempo real

### Dashboard

- Gráfico de 6 meses com Chart.js
- Cards com estatísticas (posts, drafts, comentários)
- Tabela de posts recentes
- Tabela de comentários com análise

### Notificações

- Ícone com badge de contagem na navbar
- Página dedicada com paginação
- Marcar como lida
- Histórico completo

## 🛠️ Variáveis de Ambiente Importantes

| Variável        | Descrição                      | Exemplo               |
| --------------- | ------------------------------ | --------------------- |
| `DEBUG`         | Modo debug (False em produção) | `False`               |
| `SECRET_KEY`    | Chave secreta Django           | `django-insecure-...` |
| `DB_NAME`       | Nome do banco de dados         | `velora_blog`         |
| `DB_USER`       | Usuário PostgreSQL             | `velora_user`         |
| `DB_PASSWORD`   | Senha PostgreSQL               | `sua_senha`           |
| `DB_HOST`       | Host do PostgreSQL             | `localhost`           |
| `DB_PORT`       | Porta PostgreSQL               | `5432`                |
| `ALLOWED_HOSTS` | Hosts permitidos               | `localhost,127.0.0.1` |

## ⚙️ Dependências Principais

```
Django==5.2.9
psycopg2-binary==2.9.11
Pillow==12.0.0
python-dotenv==1.2.1
python-decouple==3.8
sqlparse==0.5.4
asgiref==3.11.0
```

Veja `requirements.txt` para a lista completa.

## 🚨 Observações Importantes

1. **Segurança:** Nunca faça commit de variáveis sensíveis (senhas, `SECRET_KEY`, etc.). Use sempre um arquivo `.env` que esteja no `.gitignore`.

2. **Admin Django:** O Django Admin (`/admin/`) deve ser usado para:

   - Criar/editar posts (se necessário)
   - Gerenciar categorias e tags globalmente
   - Moderar comentários (se desabilitar aprovação automática)
   - Gerenciar usuários e permissões

3. **Site Público:** A avaliação será feita principalmente nas views públicas:

   - Lista de posts
   - Detalhe do post
   - Comentários
   - Página de usuário
   - Dashboard

4. **Rascunhos:** Posts sem data de publicação são considerados rascunhos e aparecem apenas para o autor no Dashboard.

5. **Performance:** Para produção, considere:
   - Usar `DEBUG=False`
   - Configurar HTTPS
   - Usar cache (Redis)
   - Otimizar queries (select_related, prefetch_related)

## 📞 Troubleshooting

### Erro: "psycopg2: relação 'blog_post' não existe"

- Execute: `python manage.py migrate`

### Erro: "TemplateDoesNotExist"

- Verifique se o diretório `templates/` está no mesmo nível de `manage.py`
- Verifique as configurações em `velora/settings.py`

### Erro: "Static files not found"

- Execute: `python manage.py collectstatic --noinput`

### Erro de conexão ao PostgreSQL

- Verifique se o PostgreSQL está rodando
- Verifique as credenciais no `.env`
- Teste com: `python -c "import psycopg2; psycopg2.connect('dbname=velora_blog user=velora_user password=sua_senha host=localhost')"`

## 📄 Licença

Este projeto é fornecido como está para fins educacionais.

## 👨‍💻 Autor

Desenvolvido como desafio de seleção de bolsistas.

---

**Última atualização:** Dezembro 2025
