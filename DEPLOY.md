# 🚀 Deploy do Projeto Abonadas na Nuvem

## ✅ Preparação Concluída

Seu projeto foi preparado para produção com:

### 📝 Arquivos criados/modificados:

1. **`requirements.txt`** - Lista de todas as dependências
2. **`Procfile`** - Instruções para o Render executar seu app
3. **`runtime.txt`** - Especifica a versão do Python
4. **`.gitignore`** - Previne upload de arquivos sensíveis
5. **`.env.example`** - Modelo de variáveis de ambiente
6. **`settings.py`** - Atualizado para produção com:
   - `DEBUG = False` em produção
   - `ALLOWED_HOSTS` usando variável de ambiente
   - `SECRET_KEY` usando variável de ambiente
   - Banco de dados configurado para usar `DATABASE_URL`
   - WhiteNoise para servir arquivos estáticos
   - Middlewares de segurança ativados

---

## 🎯 Próximos Passos

### 1. Criar repositório no GitHub

```bash
git init
git add .
git commit -m "Preparação para deploy em produção"
git branch -M main
git remote add origin https://github.com/seu-usuario/seu-repo.git
git push -u origin main
```

### 2. Criar conta no Render

- Acesse [render.com](https://render.com)
- Faça login com GitHub
- Clique em "New" → "Web Service"
- Selecione seu repositório

### 3. Configurar no Render

**Build Command:**
```
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

**Start Command:**
```
gunicorn abonadas.wsgi
```

### 4. Definir variáveis de ambiente no Render

Na seção "Environment" do seu app no Render, adicione:

```
DEBUG=False
SECRET_KEY=gera-uma-chave-segura-aqui-com-64-caracteres
ALLOWED_HOSTS=seu-app-abc123.onrender.com,www.seu-app-abc123.onrender.com
DATABASE_URL=postgres://usuario:senha@hostname:5432/dbname
```

---

## 🔐 Gerar SECRET_KEY Segura

Execute em Python:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Ou use um gerador online.

---

## 📊 Criar Banco de Dados no Render

1. No painel do Render, clique em "New" → "PostgreSQL"
2. Preencha com um nome
3. Clique em "Create Database"
4. Copie a URL no formato: `postgres://user:password@hostname:port/dbname`
5. Cole em `DATABASE_URL` no seu Web Service

---

## ⚠️ Segurança - Checklist

- ✅ `DEBUG = False` em produção
- ✅ `SECRET_KEY` usando variável de ambiente
- ✅ `ALLOWED_HOSTS` definido corretamente
- ✅ Banco de dados em servidor remoto
- ✅ WhiteNoise configurado para statics
- ✅ `.gitignore` previne upload de `.env`
- ✅ Cookies CSRF seguros (`CSRF_COOKIE_SECURE = True`)
- ✅ SSL redirect ativo (`SECURE_SSL_REDIRECT = True`)

---

## 🧪 Testar Localmente em Modo Produção

```bash
# Ativar o environment virtual
.\pi1\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Rodar collectstatic
python manage.py collectstatic --noinput

# Testar com DEBUG=False (não recomendado localmente, só para testes)
DEBUG=False python manage.py runserver
```

---

## 📱 URLs da sua aplicação

Após fazer o deploy, seu app estará em:

```
https://seu-app-abc123.onrender.com
```

(O nome específico aparecerá no painel do Render)

---

## 🐛 Troubleshooting

**App não sobe?** Verifique:
- `python manage.py migrate` executou sem erros
- `python manage.py collectstatic` funcionou
- Variáveis de ambiente estão definidas corretamente
- Banco de dados está acessível

**Ver logs:**
- Painel do Render → "Logs"

---

## ✨ Próxima Etapa: CI/CD (Opcional)

Depois que o deploy manual estiver funcionando por alguns dias, você pode adicionar:

1. **Testes automatizados** com `pytest`
2. **GitHub Actions** para rodar testes antes de fazer deploy
3. **Auto-deploy** quando o código passar nos testes

---

## 📞 Suporte

Dúvidas sobre:
- **Render**: [docs.render.com](https://docs.render.com)
- **Django**: [docs.djangoproject.com](https://docs.djangoproject.com)
- **PostgreSQL no Render**: [render.com/docs/postgresql](https://render.com/docs/postgresql)

Bom deploy! 🚀
