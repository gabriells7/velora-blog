from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, authenticate, login
from django.utils.text import slugify
from django.utils import timezone
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Post, Categoria, Tag, Comentario, Notification
from .forms import PostForm, UserSignUpForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DeleteView
from django.urls import reverse_lazy


class PostListView(ListView):
    queryset = Post.objects.filter(publicado_em__isnull=False).order_by('-publicado_em')
    template_name = 'home.html'
    context_object_name = 'posts'
    paginate_by = 6


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Evita filtros complexos no template
        context['comentarios_aprovados'] = self.object.comentarios.filter(aprovado=True)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        mensagem = request.POST.get('mensagem')

        if nome and email and mensagem:
            Comentario.objects.create(
                post=self.object,
                nome=nome,
                email=email,
                mensagem=mensagem,
                aprovado=True,
            )
        
        return redirect(self.request.path)


class PostsPorCategoriaView(ListView):
    template_name = 'home.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Post.objects.filter(categoria__slug=slug, publicado_em__isnull=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f"Categoria: {Categoria.objects.get(slug=self.kwargs['slug']).nome}"
        return context


class PostsPorTagView(ListView):
    template_name = 'home.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Post.objects.filter(tags__slug=slug, publicado_em__isnull=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = f"Tag: {Tag.objects.get(slug=self.kwargs['slug']).nome}"
        return context


class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True


class CustomLogoutView(TemplateView):
    template_name = 'logout.html'
    
    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


def signup(request):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # fazer login automático após signup
            login(request, user)
            return redirect('/usuario/')
    else:
        form = UserSignUpForm()
    
    context = {'form': form}
    return render(request, 'singup.html', context)


class NewPostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'new_post.html'
    success_url = '/usuario/'

    def form_valid(self, form):
        form.instance.autor = self.request.user
        
        # Se não foi fornecido um slug, gera automaticamente do título
        if not form.instance.slug:
            base_slug = slugify(form.instance.titulo)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            form.instance.slug = slug
        
        # Verifica qual botão foi clicado
        if 'salvar_rascunho' in self.request.POST:
            # Salvar como rascunho (sem data de publicação)
            form.instance.publicado_em = None
        elif 'publicar' in self.request.POST:
            # Publicar imediatamente se não foi fornecida data
            if not form.cleaned_data.get('publicado_em'):
                form.instance.publicado_em = timezone.now()
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all().order_by('nome')
        context['tags'] = Tag.objects.all().order_by('nome')
        return context



def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user

            # gerar slug se vazio
            if not post.slug:
                base_slug = slugify(post.titulo)
                slug = base_slug
                counter = 1
                while Post.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                post.slug = slug

            # lidar com salvar como rascunho / publicar
            if 'salvar_rascunho' in request.POST:
                post.publicado_em = None
            elif 'publicar' in request.POST:
                if not form.cleaned_data.get('publicado_em'):
                    post.publicado_em = timezone.now()

            post.save()
            
            # Processa categorias: verifica se é ID ou novo nome
            categoria_id = request.POST.get('categoria', '').strip()
            if categoria_id:
                # Se for um número, é um ID existente
                if categoria_id.isdigit():
                    try:
                        categoria_obj = Categoria.objects.get(pk=categoria_id)
                        post.categoria = categoria_obj
                        post.save()
                    except Categoria.DoesNotExist:
                        pass
                else:
                    # Se não for número, criar nova categoria
                    cat_slug = slugify(categoria_id)
                    categoria_obj, _ = Categoria.objects.get_or_create(slug=cat_slug, defaults={'nome': categoria_id})
                    post.categoria = categoria_obj
                    post.save()

            # Processa tags: verifica IDs selecionados e detecta novos nomes
            tags_selecionadas = request.POST.getlist('tags')
            for tag_valor in tags_selecionadas:
                tag_valor = tag_valor.strip()
                if not tag_valor:
                    continue
                
                # Se for um número, é um ID existente
                if tag_valor.isdigit():
                    try:
                        tag_obj = Tag.objects.get(pk=tag_valor)
                        post.tags.add(tag_obj)
                    except Tag.DoesNotExist:
                        pass
                else:
                    # Se não for número, criar nova tag
                    tag_slug = tag_valor.lower().replace(' ', '-')
                    tag_obj, _ = Tag.objects.get_or_create(slug=tag_slug, defaults={'nome': tag_valor})
                    post.tags.add(tag_obj)
            
            return redirect('/usuario/')
    else:
        form = PostForm()
    


    context = {
        'form': form,
        'categorias': Categoria.objects.all().order_by('nome'),
        'tags': Tag.objects.all().order_by('nome'),
    }
    return render(request, 'new_post.html', context)

    def new_comentario(request):
        if request.method == 'POST':
            post_id = request.POST.get('post_id')
            nome = request.POST.get('nome')
            email = request.POST.get('email')
            mensagem = request.POST.get('mensagem')

            post = get_object_or_404(Post, id=post_id)

            if nome and email and mensagem:
                Comentario.objects.create(
                    post=post,
                    nome=nome,
                    email=email,
                    mensagem=mensagem,
                    aprovado=False,
                )
            
            return redirect(post.get_absolute_url())


def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug, autor=request.user, publicado_em__isnull=True)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            
            # lidar com salvar como rascunho / publicar
            if 'salvar_rascunho' in request.POST:
                post.publicado_em = None
            elif 'publicar' in request.POST:
                if not form.cleaned_data.get('publicado_em'):
                    post.publicado_em = timezone.now()
            
            post.save()
            
            # Processa categorias: verifica se é ID ou novo nome
            categoria_id = request.POST.get('categoria', '').strip()
            if categoria_id:
                # Se for um número, é um ID existente
                if categoria_id.isdigit():
                    try:
                        categoria_obj = Categoria.objects.get(pk=categoria_id)
                        post.categoria = categoria_obj
                        post.save()
                    except Categoria.DoesNotExist:
                        pass
                else:
                    # Se não for número, criar nova categoria
                    cat_slug = slugify(categoria_id)
                    categoria_obj, _ = Categoria.objects.get_or_create(slug=cat_slug, defaults={'nome': categoria_id})
                    post.categoria = categoria_obj
                    post.save()

            # Processa tags: verifica IDs selecionados e detecta novos nomes
            tags_selecionadas = request.POST.getlist('tags')
            for tag_valor in tags_selecionadas:
                tag_valor = tag_valor.strip()
                if not tag_valor:
                    continue
                
                # Se for um número, é um ID existente
                if tag_valor.isdigit():
                    try:
                        tag_obj = Tag.objects.get(pk=tag_valor)
                        post.tags.add(tag_obj)
                    except Tag.DoesNotExist:
                        pass
                else:
                    # Se não for número, criar nova tag
                    tag_slug = tag_valor.lower().replace(' ', '-')
                    tag_obj, _ = Tag.objects.get_or_create(slug=tag_slug, defaults={'nome': tag_valor})
                    post.tags.add(tag_obj)
            
            return redirect('/usuario/')
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'categorias': Categoria.objects.all().order_by('nome'),
        'tags': Tag.objects.all().order_by('nome'),
        'post': post,
        'is_edit': True,
    }
    return render(request, 'new_post.html', context)


class UsuarioView(LoginRequiredMixin, TemplateView):
    template_name = 'usuario.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Posts publicados pelo usuário
        posts_publicados = Post.objects.filter(
            autor=user,
            publicado_em__isnull=False
        ).order_by('-publicado_em')[:10]
        
        # Posts não publicados (rascunhos)
        posts_rascunhos = Post.objects.filter(
            autor=user,
            publicado_em__isnull=True
        ).order_by('-criado_em')[:10]
        
        # Comentários nos posts do usuário
        comentarios_pendentes = Comentario.objects.filter(
            post__autor=user,
            aprovado=False
        ).order_by('-criado_em')[:10]
        
        context['user'] = user
        context['posts_publicados'] = posts_publicados
        context['posts_rascunhos'] = posts_rascunhos
        context['comentarios_pendentes'] = comentarios_pendentes
        context['total_posts_publicados'] = Post.objects.filter(
            autor=user,
            publicado_em__isnull=False
        ).count()
        context['total_posts_rascunhos'] = Post.objects.filter(
            autor=user,
            publicado_em__isnull=True
        ).count()
        context['total_comentarios_pendentes'] = Comentario.objects.filter(
            post__autor=user,
            aprovado=False
        ).count()

        # Estatísticas para dashboard: posts por mês (últimos 6 meses)
        from datetime import datetime
        now = datetime.now()
        months = []
        total_last_6 = 0
        for i in range(5, -1, -1):
            # calcula ano/mês retroativamente
            month = now.month - i
            year = now.year
            while month <= 0:
                month += 12
                year -= 1
            count = Post.objects.filter(
                autor=user,
                publicado_em__year=year,
                publicado_em__month=month
            ).count()
            months.append({'year': year, 'month': month, 'count': count})
            total_last_6 += count

        context['posts_by_month'] = months
        context['avg_posts_last_6_months'] = total_last_6 / 6 if total_last_6 else 0

        # Interação: comentários totais recebidos e média por post
        total_comments_received = Comentario.objects.filter(post__autor=user).count()
        context['total_comments_received'] = total_comments_received
        context['avg_comments_per_post'] = (
            total_comments_received / context['total_posts_publicados']
            if context['total_posts_publicados'] > 0 else 0
        )

        return context




from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


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



def marcar_lida(request, id):
    if request.method == 'POST':
        try:
            n = Notification.objects.get(pk=id, user=request.user)
            n.read = True
            n.save()
        except Notification.DoesNotExist:
            pass
    return redirect('blog:notificacoes')

def new_post_notification(request, post, users):
    for user in users:
        Notification.objects.create(
            user=user,
            actor=post.autor,
            title="Novo Post Publicado",
            verb=f"Um novo post intitulado '{post.titulo}' foi publicado.",
            message=f"Confira o novo post: {post.get_absolute_url()}",
        )

class delete_post(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'delete_post.html'
    success_url = '/usuario/'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.autor


def delete_comment(request, comment_id):
    comentario = get_object_or_404(Comentario, pk=comment_id)
    post = comentario.post
    
    # Verifica se o usuário é o dono do post
    if request.user != post.autor:
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    if request.method == 'POST':
        comentario.delete()
        return redirect(post.get_absolute_url())
    
    return redirect(post.get_absolute_url())


@require_http_methods(["POST"])
def criar_tag(request):

    import json
    try:
        data = json.loads(request.body)
        nome = data.get('nome', '').strip()
        
        if not nome:
            return JsonResponse({'error': 'Nome da tag é obrigatório'}, status=400)
        
        tag_slug = nome.lower().replace(' ', '-')
        tag, created = Tag.objects.get_or_create(slug=tag_slug, defaults={'nome': nome})
        
        return JsonResponse({
            'id': tag.id,
            'nome': tag.nome,
            'slug': tag.slug,
            'created': created
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def criar_categoria(request):
    import json
    try:
        data = json.loads(request.body)
        nome = data.get('nome', '').strip()
        
        if not nome:
            return JsonResponse({'error': 'Nome da categoria é obrigatório'}, status=400)
        
        cat_slug = slugify(nome)
        categoria, created = Categoria.objects.get_or_create(slug=cat_slug, defaults={'nome': nome})
        
        return JsonResponse({
            'id': categoria.id,
            'nome': categoria.nome,
            'slug': categoria.slug,
            'created': created
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def check_email(request):
    import json
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        
        if not email:
            return JsonResponse({'error': 'Email é obrigatório'}, status=400)
        
        exists = User.objects.filter(email=email).exists()
        
        return JsonResponse({
            'email': email,
            'exists': exists
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

