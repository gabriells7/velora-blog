# Velora Blog — Mudanças manuais e como aplicá-las

Este README explica passo a passo como reproduzir manualmente as alterações que foram feitas neste repositório para adicionar suporte a notificações e garantir o funcionamento da página de "Novo Post" (`new_post`).

Observação: as instruções abaixo assumem que você está usando Windows PowerShell e o ambiente virtual já está ativado (ex.: `myvenv\Scripts\Activate.ps1`).

---

## 1) Resumo das alterações feitas

- Adicionado modelo `Notification` em `blog/models.py` (campos: `user`, `actor`, `title`, `verb`, `message`, `timestamp`, `read`).
- Registrado `Notification` no `blog/admin.py` para administração via Django admin.
- Implementadas views em `blog/views.py`:
  - `notificacoes(request)` — lista paginada das notificações do usuário.
  - `marcar_lida(request, id)` — marca uma notificação como lida (via POST).
- Adicionadas rotas em `blog/urls.py`:
  - `notificacoes/` (name=`notificacoes`)
  - `notificacoes/marcar_lida/<int:id>/` (name=`marcar_lida`)
- Template `templates/notification.html` criado/atualizado com layout para exibir notificações.
- `new_post` já está disponível através de `NewPostView`, `PostForm` e `templates/new_post.html`.

---

## 2) Passo a passo: aplicar manualmente cada alteração

A seguir estão os trechos de código e instruções para aplicar cada alteração manualmente.

Atenção: faça backup dos seus arquivos antes de editar, ou use controle de versão (git).

### 2.1 Adicionar o modelo `Notification`

Edite `blog/models.py` e adicione o seguinte trecho (imediatamente após as classes existentes, por exemplo depois de `Comentario`):

```python
from django.contrib.auth.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='actor_notifications')
    title = models.CharField(max_length=200, blank=True)
    verb = models.CharField(max_length=200, blank=True)
    message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'Notification to {self.user.username}: {self.title or self.verb or self.message[:30]}'
```

Depois salve o arquivo.

### 2.2 Registrar no admin

Edite `blog/admin.py` e importe o modelo e registre-o:

```python
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'actor', 'title', 'verb', 'read', 'timestamp')
    list_filter = ('read', 'timestamp')
    search_fields = ('title', 'verb', 'message', 'user__username', 'actor__username')
```

### 2.3 Implementar as views de notificações

Edite `blog/views.py` e adicione as views (importando `Notification`, `login_required`, `Paginator`):

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Notification

@login_required
def notificacoes(request):
    qs = Notification.objects.filter(user=request.user).order_by('-timestamp')
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'notifications': page_obj.object_list,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'notification.html', context)

@login_required
def marcar_lida(request, id):
    if request.method == 'POST':
        try:
            n = Notification.objects.get(pk=id, user=request.user)
            n.read = True
            n.save()
        except Notification.DoesNotExist:
            pass
    return redirect('blog:notificacoes')
```

> Nota: ajuste importações no topo do arquivo conforme a estrutura do seu arquivo atual.

### 2.4 Adicionar as rotas

Edite `blog/urls.py` e adicione as rotas para notificações:

```python
path('notificacoes/', views.notificacoes, name='notificacoes'),
path('notificacoes/marcar_lida/<int:id>/', views.marcar_lida, name='marcar_lida'),
```

Coloque essas linhas dentro da lista `urlpatterns` (por exemplo após a rota `post/novo/`).

### 2.5 Template de notificações

Crie ou edite `templates/notification.html` com um layout básico (exemplo usado neste projeto):

- Um `list-group` Bootstrap com um loop `{% for notification in notifications %}`.
- Mostre `notification.title` / `notification.verb` / `notification.message`.
- Exiba `notification.timestamp|timesince` e um botão que submete POST para `/notificacoes/marcar_lida/{{ notification.id }}/` quando não lida.

(Existe um template exemplo no repositório; você pode copiá-lo para este arquivo.)

### 2.6 `new_post` (formulário e view)

Este projeto já inclui:

- `NewPostView` em `blog/views.py` (classe `CreateView`) que usa `PostForm`;
- `PostForm` em `blog/forms.py` com widgets e labels;
- `templates/new_post.html` com o formulário e JavaScript para preencher slug/data.

Se você precisar criar manualmente `new_post` do zero, passos mínimos:

1. Criar `PostForm` em `blog/forms.py` (ModelForm para `Post` com campos desejados).
2. Criar `NewPostView` em `blog/views.py`:

```python
class NewPostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'new_post.html'
    success_url = '/usuario/'

    def form_valid(self, form):
        form.instance.autor = self.request.user
        # gerar slug se vazio e lógica de publicação já vista no repositório
        return super().form_valid(form)
```

3. Adicionar rota em `blog/urls.py`:

```python
path('post/novo/', views.NewPostView.as_view(), name='novo_post'),
```

4. Criar `templates/new_post.html` com `{{ form }}` e botões `salvar_rascunho` e `publicar` (o template deste repo já implementa isso).

---

## 3) Comandos para gerar migrações, aplicar e testar

No PowerShell (com o ambiente virtual ativado), rode:

```powershell
py manage.py makemigrations
py manage.py migrate
py manage.py createsuperuser   # se precisar de um usuário admin
py manage.py runserver
```

### Criar uma notificação de teste via shell

```powershell
py manage.py shell
>>> from django.contrib.auth.models import User
>>> from blog.models import Notification
>>> u = User.objects.first()
>>> Notification.objects.create(user=u, verb='Teste', message='Notificação de teste')
>>> exit()
```

Acesse `http://127.0.0.1:8000/notificacoes/` enquanto estiver logado como esse usuário.

---

## 4) Como marcar notificações como lidas

- Pelo admin: acesse `/admin/` e marque campo `read`.
- Pelo template: o botão de cada notificação submete um `POST` para `/notificacoes/marcar_lida/<id>/` que chama a view `marcar_lida` e atualiza o campo `read`.

---

## 5) Ajustes opcionais sugeridos

- Criar um Context Processor para incluir a contagem de notificações não lidas em todas as templates e mostrar no navbar.
- Adicionar links nas notificações para objetos relacionados (ex.: post) e ajustar `Notification` para guardar `content_type`/`object_id` (GenericForeignKey) se quiser flexibilidade.
- Usar sinais (signals) para criar notificações automaticamente quando ocorrerem eventos (novo comentário, menção, etc.).

---

## 6) Perguntas e próximos passos

Se você quiser, eu posso:

- Gerar as migrações automaticamente agora (executar `makemigrations` e `migrate`).
- Criar um context processor para a contagem de não-lidas e atualizar `base.html`.
- Adicionar um `GenericForeignKey` para vincular notificações a objetos do site.

Diga qual desses próximos passos prefere que eu faça.
