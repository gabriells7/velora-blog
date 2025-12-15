from django.contrib import admin
from .models import Post, Categoria, Tag, Comentario
from .models import Notification


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug')
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ('nome',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug')
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ('nome',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'criado_em', 'publicado_em')
    list_filter = ('categoria', 'tags', 'autor', 'criado_em')
    search_fields = ('titulo', 'conteudo')
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'criado_em'
    filter_horizontal = ('tags',)


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'post', 'criado_em', 'aprovado')
    list_filter = ('aprovado', 'criado_em')
    search_fields = ('nome', 'email', 'mensagem')
    actions = ['aprovar_comentarios']

    def aprovar_comentarios(self, request, queryset):
        queryset.update(aprovado=True)
    aprovar_comentarios.short_description = "Aprovar comentários selecionados"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'actor', 'title', 'verb', 'read', 'timestamp')
    list_filter = ('read', 'timestamp')
    search_fields = ('title', 'verb', 'message', 'user__username', 'actor__username')