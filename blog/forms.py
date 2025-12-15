from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Categoria, Tag


class UserSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg'}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'}))
    password2 = forms.CharField(label='Confirmar Senha', widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está registrado.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este usuário já existe.')
        return username


# Custom fields que não validam choices (permite criar novas categorias/tags)
class NoValidationMultipleChoiceField(forms.ModelMultipleChoiceField):
    def validate(self, value):
        # Permite valores que não existem (serão criados na view)
        pass


class NoValidationChoiceField(forms.ModelChoiceField):
    def validate(self, value):
        # Permite valores que não existem (serão criados na view)
        pass


class PostForm(forms.ModelForm):
    nova_tag = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite uma nova tag e pressione Enter'
        }),
        help_text='Crie uma tag digitando o nome e pressionando Enter'
    )

    nova_categoria = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite uma nova categoria e pressione Enter'
        }),
        help_text='Crie uma categoria digitando o nome e pressionando Enter'
    )

    class Meta:
        model = Post
        fields = ['titulo', 'slug', 'categoria', 'tags', 'conteudo', 'imagem', 'publicado_em']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 15}),
            'imagem': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'publicado_em': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
        labels = {
            'titulo': 'Título',
            'slug': 'Slug (URL amigável)',
            'categoria': 'Categoria',
            'tags': 'Tags',
            'conteudo': 'Conteúdo',
            'imagem': 'Imagem',
            'publicado_em': 'Data de Publicação (deixe em branco para salvar como rascunho)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Substitui os campos de choice para não validar valores inexistentes
        self.fields['categoria'] = NoValidationChoiceField(
            queryset=Categoria.objects.all().order_by('nome'),
            required=False,
            widget=forms.Select(attrs={'class': 'form-select'})
        )
        self.fields['tags'] = NoValidationMultipleChoiceField(
            queryset=Tag.objects.all().order_by('nome'),
            required=False,
            widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'})
        )
        self.fields['slug'].required = False
        self.fields['publicado_em'].required = False
