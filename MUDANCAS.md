# 📋 Resumo das Mudanças no Projeto

## ✅ O que foi modificado em `settings.py`

### 1. **Imports Adicionados**
```python
import os
import dj_database_url
from decouple import config
```

- `dj_database_url`: Facilita ler `DATABASE_URL` (formato PostgreSQL)
- `decouple`: Carrega variáveis de ambiente do arquivo `.env`

---

### 2. **SECRET_KEY - Agora via Variável de Ambiente**

**Antes (Inseguro):**
```python
SECRET_KEY = 'django-insecure-z79=y(9n^2%8t80@o!f0q0=($_k2qbmxr6$4^2i#z85-7**rr_'
```

**Depois (Seguro):**
```python
SECRET_KEY = config('SECRET_KEY', default='django-insecure-z79=y(9n^2%8t80@o!f0q0=($_k2qbmxr6$4^2i#z85-7**rr_')
```

- Em produção (Render): Lê a chave de uma variável de ambiente
- Em desenvolvimento local: Usa o padrão se `.env` não existir

---

### 3. **DEBUG - Agora Configurável**

**Antes:**
```python
DEBUG = True  # Sempre True (perigoso em produção!)
```

**Depois:**
```python
DEBUG = config('DEBUG', default=True, cast=bool)
```

- Em produção: `DEBUG=False` (variável no Render)
- Em desenvolvimento: `DEBUG=True` (padrão)

**Por que?** Em produção com `DEBUG=True`, Django mostra detalhes sensíveis (banco de dados, caminhos, etc.)

---

### 4. **ALLOWED_HOSTS - Segurança contra Host Header Injection**

**Antes:**
```python
ALLOWED_HOSTS = []  # Rejeita todas as requisições!
```

**Depois:**
```python
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')
```

- Local: `['localhost', '127.0.0.1']`
- Produção no Render: `['seu-app-abc123.onrender.com']`

**Exemplo de configuração no Render:**
```
ALLOWED_HOSTS=seu-app-abc123.onrender.com,www.seu-app-abc123.onrender.com
```

---

### 5. **MIDDLEWARE - Adicionado WhiteNoise**

**Antes:**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ...
]
```

**Depois:**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← NOVO
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ...
]
```

**Por quê?** WhiteNoise serve arquivos estáticos (CSS, JS, imagens) de forma eficiente em produção

---

### 6. **DATABASES - Suporta DATABASE_URL**

**Antes:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '123',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}
```

**Depois:**
```python
if config('DATABASE_URL', default=None):
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='postgres'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default='123'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432')
        }
    }
```

**Lógica:**
- Se `DATABASE_URL` estiver definida (produção): usa ela
- Senão: usa variáveis individuais `DB_NAME`, `DB_USER`, etc

**Exemplo `DATABASE_URL`:**
```
postgres://postgres:senha123@db.render.com:5432/abonadas_prod
```

---

### 7. **STATIC_FILES - Agora com WhiteNoise Storage**

**Adicionado:**
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**O que faz:**
- Comprime CSS e JS
- Cacheia versões (adiciona hash ao nome)
- Servidor web serve de forma ultra-rápida

---

### 8. **Segurança Extra - Quando `DEBUG = False`**

**Adicionado:**
```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
    }
```

**O que significa:**
- `SECURE_SSL_REDIRECT`: Força HTTPS
- `SESSION_COOKIE_SECURE`: Cookies só via HTTPS
- `CSRF_COOKIE_SECURE`: Cookie CSRF só via HTTPS
- `SECURE_BROWSER_XSS_FILTER`: Proteção contra XSS
- `SECURE_CONTENT_SECURITY_POLICY`: Apenas conteúdo da aplicação (não externo)

---

## 📦 Arquivos Criados

### `Procfile`
```
release: python manage.py migrate
web: gunicorn abonadas.wsgi
```
- `release`: Corre migrations antes de iniciar
- `web`: Inicia o servidor gunicorn

### `.gitignore`
Previne upload acidental de:
- `*.env` (variáveis de ambiente)
- `*.pyc` (arquivos compilados)
- `db.sqlite3` (banco de desenvolvimento)
- `venv/` e `pi1/` (ambientes virtuais)

### `runtime.txt`
```
python-3.11.9
```
Especifica a versão do Python para o Render

### `.env.example`
Modelo de variáveis de ambiente. Usuário copia para `.env` (local) ou configura no painel da nuvem.

---

## 🔄 Como Funciona Localmente vs Produção

### 🏠 DESENVOLVIMENTO LOCAL

```bash
# Arquivo .env (NÃO subir para GitHub!)
DEBUG=True
SECRET_KEY=chave-insegura-de-desenvolvimento
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://postgres:123@localhost:5432/postgres
```

```bash
python manage.py runserver
# Django lê .env → funciona normalmente
```

---

### ☁️ PRODUÇÃO NO RENDER

```
Variáveis de ambiente no painel do Render:
DEBUG=False
SECRET_KEY=chave-super-segura-gerada
ALLOWED_HOSTS=seu-app-abc123.onrender.com
DATABASE_URL=postgres://user:pass@db.render.com:5432/abonadas
```

```bash
gunicorn abonadas.wsgi
# Django lê variáveis do Render → funciona seguro
```

---

## ✨ Próximas Ações

1. **Subir para GitHub** (com `.gitignore` protegendo `.env`)
2. **Criar conta Render** e conectar repositório
3. **Definir variáveis de ambiente** no painel Render
4. **Criar banco PostgreSQL** no Render
5. **Deploy** automático!

---

## 🚨 Lembrete Importante

**NUNCA faça commit do arquivo `.env`!**

Está protegido pelo `.gitignore`, mas sempre revise antes de fazer push:

```bash
git status
# Se ver .env, você cometeu erro!
```

---

## 📚 Referências

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)
- [Render Django Guide](https://render.com/docs/deploy-django)
- [Decouple Documentation](https://github.com/henriquebastos/python-decouple)
