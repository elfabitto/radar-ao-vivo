# Configuração para o Render

Para resolver o problema de bloqueio do SofaScore no Render, você precisa modificar a configuração do seu serviço para usar a versão otimizada para web da aplicação.

## Passos para configurar o Render:

1. **Faça login no dashboard do Render** e acesse seu serviço web.

2. **Modifique o Start Command**:
   - Atual: `gunicorn app:app`
   - Novo: `gunicorn -c gunicorn_web.conf.py`

   Isso fará com que o Render use o arquivo `app_web.py` (especificado no `gunicorn_web.conf.py`) em vez do `app.py`.

3. **Adicione uma variável de ambiente**:
   - Nome: `PRODUCTION`
   - Valor: `true`

   Isso ativará as estratégias específicas para web no `app_web.py`.

4. **Aumente o timeout do Render** (se possível):
   - O Render tem um timeout padrão para requisições, que pode ser muito curto para algumas das estratégias implementadas.
   - Se possível, aumente esse timeout nas configurações do serviço.

5. **Atualize os requisitos**:
   - Certifique-se de que o arquivo `requirements.txt` inclui todas as novas dependências:
     - `cloudscraper`
     - `fake-useragent`

6. **Implante as alterações**:
   - Faça commit de todas as alterações no seu repositório.
   - O Render deve detectar automaticamente as alterações e reimplantar o serviço.

## Verificação:

Após a implantação, você pode verificar se a aplicação está funcionando corretamente acessando:

- A rota principal: `https://seu-app.onrender.com/`
- A rota de saúde: `https://seu-app.onrender.com/health`

Se a aplicação estiver funcionando corretamente, você verá jogos ao vivo na rota principal e um status "ok" na rota de saúde.

## Solução alternativa (se o Render não suportar arquivos de configuração do Gunicorn):

Se o Render não suportar o uso de arquivos de configuração do Gunicorn, você pode modificar o Start Command para:

```
gunicorn app_web:app --workers=4 --threads=2 --timeout=120 --bind=0.0.0.0:$PORT
```

Isso usará diretamente o `app_web.py` com configurações semelhantes às definidas no arquivo `gunicorn_web.conf.py`.

## Monitoramento:

Após a implantação, monitore os logs do Render para verificar se a aplicação está conseguindo obter dados do SofaScore ou se está usando o fallback para dados de exemplo.

Se você continuar enfrentando problemas, considere:

1. **Usar um serviço de proxy pago**:
   - Obtenha uma chave API de um serviço como ScraperAPI, ScrapingBee ou Bright Data.
   - Adicione a chave API como uma variável de ambiente no Render.
   - Modifique a função `usar_servico_proxy()` no arquivo `app_web.py` para usar a chave API.

2. **Usar uma API alternativa de futebol**:
   - Obtenha uma chave API de um serviço como API-Football, Football-Data.org ou SportMonks.
   - Adicione a chave API como uma variável de ambiente no Render.
   - Modifique a função `buscar_api_alternativa()` no arquivo `app_web.py` para usar a chave API.
