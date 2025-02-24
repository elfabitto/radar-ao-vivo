# Radar ao Vivo

Aplicação para acompanhar jogos de futebol ao vivo.

## Problema de Bloqueio Anti-Scraping

O SofaScore implementa medidas anti-scraping que podem bloquear requisições, especialmente quando a aplicação é implantada na web. Isso ocorre porque os provedores de hospedagem na web geralmente têm IPs que são conhecidos e bloqueados por sites como o SofaScore.

## Soluções Implementadas

Foram criadas duas versões da aplicação:

1. **app.py**: Versão padrão que funciona bem localmente, usando técnicas básicas para contornar o bloqueio.
2. **app_web.py**: Versão otimizada para implantação na web, com estratégias adicionais para contornar o bloqueio.

### Estratégias Implementadas

- **Rotação de User-Agents**: Uso da biblioteca fake-useragent para gerar User-Agents aleatórios e realistas.
- **Cloudscraper**: Biblioteca especializada em contornar proteções anti-bot como Cloudflare.
- **Simulação de Navegação**: Acesso a múltiplas páginas do site antes de acessar a API para simular comportamento humano.
- **Headers Completos**: Adição de headers mais realistas para simular um navegador real.
- **Delays Aleatórios**: Implementação de delays entre requisições para simular comportamento humano.
- **Fallback para Dados de Exemplo**: Se todas as estratégias falharem, a aplicação exibe dados de exemplo para não quebrar a UI.

## Execução Local

Para executar a aplicação localmente:

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar a aplicação
python app.py
```

A aplicação estará disponível em http://127.0.0.1:5000

## Implantação na Web

### Implantação Local

Para implantar a aplicação localmente, use o arquivo de configuração do Gunicorn otimizado para produção:

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar com Gunicorn usando a configuração para web
gunicorn -c gunicorn_web.conf.py
```

Este arquivo de configuração:
- Define a variável de ambiente `PRODUCTION=true` para ativar estratégias específicas para web
- Configura o número adequado de workers e threads
- Define timeouts mais longos para lidar com requisições que podem demorar mais
- Configura logs detalhados para monitoramento

### Implantação no Render

Para implantar a aplicação no Render, você tem duas opções:

#### Opção 1: Usar o arquivo render.yaml (recomendado)

1. Certifique-se de que o arquivo `render.yaml` está no diretório raiz do seu repositório.
2. Conecte seu repositório ao Render.
3. O Render detectará automaticamente o arquivo `render.yaml` e configurará o serviço de acordo.

#### Opção 2: Configuração manual

Se preferir configurar manualmente, siga as instruções no arquivo `render_config.md`.

Em resumo:
1. Modifique o Start Command para: `gunicorn app_web:app --workers=4 --threads=2 --timeout=120 --bind=0.0.0.0:$PORT`
2. Adicione a variável de ambiente `PRODUCTION=true`
3. Certifique-se de que o arquivo `requirements.txt` inclui todas as dependências necessárias

## Opções Adicionais para Contornar Bloqueios

Se a aplicação continuar enfrentando bloqueios na web, considere:

1. **Serviços de Proxy Pagos**: Serviços como ScraperAPI, ScrapingBee ou Bright Data oferecem IPs rotacionados e limpos que podem contornar bloqueios. Para usar, obtenha uma chave API e configure na função `usar_servico_proxy()` no arquivo app_web.py.

2. **APIs Alternativas**: Considere usar APIs oficiais de futebol como:
   - [API-Football](https://www.api-football.com/)
   - [Football-Data.org](https://www.football-data.org/)
   - [SportMonks](https://www.sportmonks.com/)

   Para implementar, obtenha uma chave API e configure na função `buscar_api_alternativa()` no arquivo app_web.py.

3. **Hospedagem em VPS**: Hospedar a aplicação em um VPS (Virtual Private Server) em vez de plataformas PaaS pode dar mais controle sobre o IP e permitir o uso de proxies ou VPNs.

## Testando Estratégias

A aplicação web inclui uma rota para testar estratégias específicas:

```
/test_strategy/<strategy>
```

Onde `<strategy>` pode ser:
- `cloudscraper`: Testa a estratégia usando cloudscraper
- `servico_proxy`: Testa a estratégia usando serviço de proxy
- `api_alternativa`: Testa a estratégia usando API alternativa
- `fontes_publicas`: Testa a estratégia usando fontes públicas

## Monitoramento

A aplicação web inclui uma rota para verificar o status do servidor:

```
/health
```

Esta rota retorna o status do servidor e um timestamp, útil para monitoramento e health checks.
