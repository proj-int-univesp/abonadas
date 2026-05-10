# 🎬 Guia Visual: Configurando no Render

## Passo 1: Criar Web Service

1. Acesse [render.com](https://render.com) e faça login com GitHub
2. Clique em "+ New"
3. Selecione "Web Service"
4. Escolha o repositório `seu-usuario/abonadas`

---

## Passo 2: Configurar Build & Deploy

Na página de criação do Web Service:

### Nome do Serviço
```
abonadas  (ou outro nome que preferir)
```

### Repository
```
seu-usuario/abonadas
```

### Branch
```
main
```

### Root Directory
```
(deixar em branco)
```

### Environment
```
Python 3
```

### Build Command
```
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

### Start Command
```
gunicorn abonadas.wsgi
```

---

## Passo 3: Adicionar Variáveis de Ambiente

Antes de criar, clique em "Add Environment Variable"

### Variável 1: DEBUG
```
Key: DEBUG
Value: False
```

### Variável 2: SECRET_KEY
```
Key: SECRET_KEY
Value: (veja como gerar abaixo)
```

### Variável 3: ALLOWED_HOSTS
```
Key: ALLOWED_HOSTS
Value: seu-app-abc123.onrender.com,www.seu-app-abc123.onrender.com
```

**Nota:** O Render vai gerar um domínio como `seu-app-abc123.onrender.com`. Use exatamente esse domínio aqui.

### Variável 4: DATABASE_URL
```
Key: DATABASE_URL
Value: postgres://user:password@hostname:port/dbname
```

**Você preenchera isto DEPOIS de criar o banco PostgreSQL**

---

## 🔑 Como Gerar SECRET_KEY

### Opção 1: Python Direto

Abra Python e execute:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Output exemplo:
```
u9^o$w@n-m1m^2h3$x0#=^*_+0&b@!=u5^3$%8d#q!8@#*0&!
```

### Opção 2: Gerador Online

Use um site como [Django Secret Key Generator](https://djecrety.ir/)

Copie a chave gerada.

---

## 🗄️ Criar Banco de Dados PostgreSQL

### Passo 1: Novo PostgreSQL

1. De volta ao painel do Render
2. Clique em "+ New"
3. Selecione "PostgreSQL"

### Passo 2: Configurar

```
Name: abonadas-db
```

### Passo 3: Criar

Clique em "Create Database"

---

## 📋 Copiar DATABASE_URL

Após criar o banco:

1. Na página do banco, você verá uma URL como:
   ```
   postgres://user_123:password_abc123@dpg-xyz.render.com:5432/abonadas_db_xyz
   ```

2. Copie essa URL

3. Volte para seu Web Service (abonadas)

4. Na seção "Environment", edite `DATABASE_URL`

5. Cole a URL

---

## ✅ Checklist Final Antes de Criar

- [ ] Repositório GitHub com código pronto
- [ ] Procfile criado
- [ ] requirements.txt gerado
- [ ] Domínio do Render anotado (ex: seu-app-abc123.onrender.com)
- [ ] SECRET_KEY gerada e copiada
- [ ] Banco PostgreSQL criado
- [ ] DATABASE_URL copiada do banco
- [ ] Todas as 4 variáveis de ambiente prontas

---

## 🚀 Criar o Web Service

1. Preencha todas as informações acima
2. Clique em "Create Web Service"
3. Render começará o build automaticamente

---

## 📊 Acompanhar o Deploy

Na página do seu Web Service:

1. Abra a aba "Logs"
2. Você verá algo como:

```
Building Docker image...
Running build command...
pip install -r requirements.txt...
python manage.py collectstatic --noinput...
python manage.py migrate...
Starting server: gunicorn abonadas.wsgi
```

3. Se ver `running on` = está pronto!

---

## ✨ Seu App Está Online!

O Render vai lhe dar uma URL como:

```
https://seu-app-abc123.onrender.com
```

**Acesse em qualquer navegador e teste seu app!** 🎉

---

## ❌ Erros Comuns

### Erro: "No module named 'dj_database_url'"
**Causa:** requirements.txt não foi instalado
**Solução:** Verifique se o `pip install -r requirements.txt` rodou sem erros

### Erro: "Database is not accessible"
**Causa:** DATABASE_URL está errada
**Solução:** Copie novamente do PostgreSQL que você criou

### Erro: "Static files not found"
**Causa:** `python manage.py collectstatic` falhou
**Solução:** Verifique os logs, é geralmente problema com STATIC_DIRS

### Erro: "Bad Request (400)"
**Causa:** ALLOWED_HOSTS não tem seu domínio
**Solução:** Copie exatamente o domínio que o Render gerou

---

## 🔄 Atualizar Depois

Sempre que mudar o código:

```bash
git add .
git commit -m "mensagem"
git push origin main
```

Render detectará automaticamente e fará novo deploy! 🎯

---

## 📱 Teste no Celular

Para testar em um celular/outro dispositivo:

1. Seu app está em: `https://seu-app-abc123.onrender.com`
2. Se o celular está conectado na mesma rede que seu PC, mas estiver fora do Brasil (VPN bloqueando), tente acessar o domínio direto
3. Render fornece HTTPS, então é seguro

---

## 🎓 Resumo Visual

```
GitHub
   ↓
Render detecta push
   ↓
Instala dependências (pip install -r requirements.txt)
   ↓
Coleta arquivos estáticos (collectstatic)
   ↓
Roda migrations (python manage.py migrate)
   ↓
Inicia servidor (gunicorn abonadas.wsgi)
   ↓
App online em: https://seu-app-abc123.onrender.com
```

Pronto! 🚀
