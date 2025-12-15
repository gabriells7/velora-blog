# blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='lista_posts'),
    path('post/novo/', views.new_post, name='novo_post'),
    path('post/<slug:slug>/editar/', views.edit_post, name='editar_post'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='detalhe_post'),
    path('categoria/<slug:slug>/', views.PostsPorCategoriaView.as_view(), name='posts_por_categoria'),
    path('tag/<slug:slug>/', views.PostsPorTagView.as_view(), name='posts_por_tag'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('usuario/', views.UsuarioView.as_view(), name='usuario'),
    path('dashboard/', views.UsuarioView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('notificacoes/', views.notificacoes, name='notificacoes'),
    path('notificacoes/marcar_lida/<int:id>/', views.marcar_lida, name='marcar_lida'),
    path('post/<int:pk>/delete/', views.delete_post.as_view(), name='post_delete'),
    path('comentario/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('api/criar-tag/', views.criar_tag, name='criar_tag'),
    path('api/criar-categoria/', views.criar_categoria, name='criar_categoria'),
    path('api/check-email/', views.check_email, name='check_email'),
]