# 🔄 Fluxo de Trabalho: Desenvolvimento → Render

## Após o primeiro deploy estar funcionando

Aqui está como você desenvolve, testa e faz deploy daqui para frente:

---

## 📝 Workflow Diário

### 1️⃣ Desenvolvimento Local

```bash
# Certifique-se que está no branch main e atualizado
git checkout main
git pull origin main

# Faça suas mudanças no código
# Edite arquivos, crie features, etc...

# Teste localmente
python manage.py runserver
# Acesse http://127.0.0.1:8000 e teste
```

### 2️⃣ Preparar Commit

```bash
# Ver o que mudou
git status

# Adicionar mudanças
git add .

# Ou adicionar seletivamente
git add abon_app/views.py  # arquivo específico
git add abon_app/          # pasta específica
```

### 3️⃣ Fazer Commit

```bash
# Commit com mensagem clara
git commit -m "Adiciona novo relatório de vendas"

# Boas práticas de mensagem:
# - Use português ou inglês de forma consistente
# - Seja descritivo
# - Use imperativo: "Adiciona", "Corrige", "Remove"

# Exemplos:
git commit -m "Adiciona validação de email"
git commit -m "Corrige bug em filtro de datas"
git commit -m "Atualiza dependências"
```

### 4️⃣ Fazer Push (Deploy Automático!)

```bash
git push origin main
```

**Pronto!** Render detecta o push e:
- ✅ Roda o build
- ✅ Instala dependências
- ✅ Roda migrations
- ✅ Coleta statics
- ✅ Inicia servidor

Seu app atualiza automaticamente! 🎉

---

## ⏱️ Quanto Tempo Leva?

```
git push
    ↓
Render detecta (1-2 segundos)
    ↓
Build inicia (5-10 segundos)
    ↓
pip install (30-60 segundos)
    ↓
collectstatic (10-20 segundos)
    ↓
migrations (5-10 segundos)
    ↓
Server inicia (5 segundos)
    ↓
App online (Total: 2-3 minutos)
```

---

## 📊 Monitorar Deploy

### Ver logs em tempo real:

1. Acesse seu Web Service no Render
2. Clique em "Logs"
3. Você verá algo como:

```
Building Docker image...
Step 1/5 : FROM python:3.11
Step 2/5 : COPY requirements.txt .
Step 3/5 : RUN pip install -r requirements.txt
  ...
  Successfully installed Django-5.1.7 ...
Step 4/5 : COPY . .
Step 5/5 : CMD ["gunicorn", "abonadas.wsgi"]
Built successfully

Running migrations...
Running 0001_initial...
Migrations completed

Collecting static files...
Collected 123 static files
Successfully collected

Running server: gunicorn abonadas.wsgi
Started server on 0.0.0.0:10000
```

### ❌ Se der erro:

O Render vai mostrar onde falhou. Exemplos:

```
Error: ModuleNotFoundError: No module named 'dj_database_url'
→ Esqueceu de adicionar em requirements.txt

Error: django.core.exceptions.ImproperlyConfigured
→ Variável de ambiente não configurada

Error: ProgrammingError: relation "abon_app_..." does not exist
→ Migration falhou, verifique o banco
```

---

## ✅ Checklist de Qualidade

Antes de fazer push, pergunte-se:

- [ ] Testei a mudança localmente?
- [ ] A mudança segue o padrão do projeto?
- [ ] Adicionei comentários se necessário?
- [ ] Removi código debugado ou TODO?
- [ ] A mensagem de commit é clara?
- [ ] Não commitei arquivo sensível (.env, db.sqlite3)?

---

## 🔧 Cenários Comuns

### Esqueci de migração

```bash
# Criar migration
python manage.py makemigrations

# Aplicar localmente
python manage.py migrate

# Commit
git add abon_app/migrations/
git commit -m "Adiciona campo X ao modelo Y"

# Push
git push origin main
# Render roda migration automaticamente
```

### Esqueci de adicionar dependência

```bash
# Instalar localmente
pip install nova-dependencia

# Adicionar a requirements.txt
pip freeze > requirements.txt

# Commit
git add requirements.txt
git commit -m "Adiciona nova-dependencia"

# Push
git push origin main
# Render instala automaticamente
```

### Preciso fazer rollback

```bash
# Ver histórico
git log --oneline
# Output:
# abc1234 Adiciona novo relatório (tem bug!)
# def5678 Corrige validação de email
# ghi9012 Deploy anterior

# Voltar para commit anterior
git revert abc1234

# Isso cria um novo commit que desfaz o anterior
git push origin main
# Render faz deploy da versão anterior
```

### Quero atualizar logo sem teste

**NÃO FAÇA ISTO!**

Sempre teste localmente primeiro:

```bash
python manage.py runserver
# Verifique em http://127.0.0.1:8000

# Ou roda em "modo produção":
DEBUG=False python manage.py runserver
```

---

## 📚 Boas Práticas

### ✅ SIM - Faça commits pequenos

```
Commit 1: Adiciona modelo de Produto
Commit 2: Adiciona view de listagem
Commit 3: Adiciona template de produto
Commit 4: Adiciona CSS do produto
```

Cada commit é fácil de entender e reverter se necessário.

### ❌ NÃO - Commits gigantes

```
Commit 1: "Várias mudanças"
  (contém 50 arquivos modificados, 1000 linhas)
```

Difícil de revisar, difícil de reverter parcialmente.

---

### ✅ SIM - Mensagens claras

```
"Adiciona autenticação de dois fatores"
"Corrige vazamento de memória em cache"
"Atualiza Django de 4.2 para 5.1"
```

### ❌ NÃO - Mensagens vagas

```
"Mudanças"
"Fix"
"Ajustes"
"wip"
```

---

## 🚨 Emergência: App Online Quebrada

Se fez push e algo deu errado:

### Opção 1: Rollback Imediato (Recomendado)

```bash
# Voltar para commit anterior
git revert HEAD

# Ou se for muito ruim:
git reset --hard HEAD~1

# Push a versão anterior
git push origin main
# Render faz deploy da versão anterior
```

### Opção 2: Pausar Deploy no Render

1. Painel do Render
2. Seu Web Service
3. "Settings"
4. "Auto-Deploy" → Desativar
5. Agora você controla quando fazer deploy

---

## 📈 Escala: Múltiplos Desenvolvedores

Se trabalhar em equipe:

```bash
# Criar branch para sua feature
git checkout -b feature/novo-relatorio

# Desenvolver...
git add .
git commit -m "Implementa novo relatório"

# Fazer Pull Request (GitHub)
git push origin feature/novo-relatorio

# Alguém revisa no GitHub
# Depois faz merge para main

# Render detecta mudança em main
# Faz deploy automaticamente
```

---

## 🎯 Fluxo Completo de 1 Semana

**Segunda:**
```bash
git push origin main # Feature 1 online
```

**Quarta:**
```bash
git push origin main # Bugfix online
```

**Sexta:**
```bash
git push origin main # Melhoria de performance online
```

**Todo dia:**
Todos podem ver as mudanças em produção dentro de 2-3 minutos! 🚀

---

## 📱 Resumo Gráfico

```
Seu computador              GitHub              Render (Nuvem)
    │                         │                      │
    ├─ Edita código           │                      │
    │                         │                      │
    ├─ git add .              │                      │
    │                         │                      │
    ├─ git commit             │                      │
    │                         │                      │
    ├─ git push ─────────────→│                      │
    │                         │                      │
    │                         ├─ Webhook trigger ──→│
    │                         │                      │
    │                         │     ├─ Build      ←─┤
    │                         │     ├─ Test       ←─┤
    │                         │     ├─ Deploy     ←─┤
    │                         │                      │
    │                         │ ← App Online! ──────┤
    │
    └─ Acessa em produção ─→ URL está atualizada
```

---

## ✨ Conclusão

Depois do primeiro deploy:

1. **Desenvolva normalmente** no seu PC
2. **Teste localmente**
3. **Commit + Push**
4. **Render faz deploy automático**
5. **Seu app atualiza em 2-3 minutos!**

**Não precisa fazer nada manualmente na nuvem!** 🎉

Bom desenvolvimento! 🚀
