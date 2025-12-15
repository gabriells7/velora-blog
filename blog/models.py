from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.models import User


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse('blog:posts_por_categoria', args=[self.slug])


class Tag(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse('blog:posts_por_tag', args=[self.slug])


class Post(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    conteudo = models.TextField()
    imagem = models.ImageField(upload_to='posts/%Y/%m/%d/', blank=True, null=True)
    criado_em = models.DateTimeField(default=timezone.now)
    publicado_em = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-publicado_em', '-criado_em']

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('blog:detalhe_post', args=[self.slug])


class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    site = models.URLField(blank=True, null=True)
    mensagem = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    aprovado = models.BooleanField(default=False)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f'Comentário de {self.nome} em {self.post.titulo}'


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
    
class NewPostNotification(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='new_post_notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='new_post_user_notifications')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'New Post Notification to {self.user.username} for post {self.post.titulo}'
    
class NewPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='new_posts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'New Post: {self.post.titulo}'


class Usuario(models.Model):
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=250)
    criado_em = models.DateTimeField(auto_now_add=True)