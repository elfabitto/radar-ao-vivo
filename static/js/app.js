// Configurações de paginação
const JOGOS_POR_PAGINA = 10;
let paginaAtual = 1;

// Função para atualizar os dados dos jogos
// Objeto para armazenar os placares anteriores
const placaresAnteriores = {};

// Função para atualizar a paginação
function atualizarPaginacao(totalJogos) {
    const totalPaginas = Math.ceil(totalJogos / JOGOS_POR_PAGINA);
    const paginationContainer = document.querySelector('.pagination');
    
    if (!paginationContainer) return;
    
    let html = '';
    
    // Botão voltar para primeira página
    html += `<button class="pagination__btn" ${paginaAtual === 1 ? 'disabled' : ''} onclick="mudarPagina(1)">Primeira</button>`;
    
    // Botão anterior
    html += `<button class="pagination__btn" ${paginaAtual === 1 ? 'disabled' : ''} onclick="mudarPagina(${paginaAtual - 1})">Anterior</button>`;
    
    // Número da página atual
    html += `<span class="pagination__info">${paginaAtual} de ${totalPaginas}</span>`;
    
    // Botão próximo
    html += `<button class="pagination__btn" ${paginaAtual >= totalPaginas ? 'disabled' : ''} onclick="mudarPagina(${paginaAtual + 1})">Próximo</button>`;
    
    paginationContainer.innerHTML = html;
}

// Função para mudar de página
function mudarPagina(novaPagina) {
    const matchRows = document.querySelectorAll('.match-row');
    const totalJogos = matchRows.length;
    const totalPaginas = Math.ceil(totalJogos / JOGOS_POR_PAGINA);
    
    if (novaPagina < 1 || novaPagina > totalPaginas) return;
    
    paginaAtual = novaPagina;
    
    // Calcular índices dos jogos a serem mostrados
    const inicio = (paginaAtual - 1) * JOGOS_POR_PAGINA;
    const fim = inicio + JOGOS_POR_PAGINA;
    
    // Processar todos os jogos de uma vez
    matchRows.forEach((row, index) => {
        const isVisible = index >= inicio && index < fim;
        
        // Definir visibilidade do jogo
        if (isVisible) {
            row.style.display = 'flex';
            row.style.opacity = '1';
            row.style.height = 'auto';
            
            // Recarregar o radar apenas se estiver visível
            const radarContainer = row.querySelector('.radar-container');
            const iframe = radarContainer.querySelector('iframe');
            const matchId = row.getAttribute('data-event-id');
            
            // Adicionar timestamp para evitar cache
            const timestamp = new Date().getTime();
            const widgetUrl = `https://widgets.sofascore.com/pt-BR/embed/attackMomentum?id=${matchId}&widgetTheme=light&_=${timestamp}`;
            
            // Remover e recriar o iframe para forçar o recarregamento
            const newIframe = document.createElement('iframe');
            newIframe.width = '50%';
            newIframe.height = '100';
            newIframe.frameBorder = '-5';
            newIframe.scrolling = 'no';
            newIframe.src = widgetUrl;
            newIframe.onload = () => checkWidget(newIframe, matchId);
            newIframe.onerror = () => showError(matchId);
            
            // Substituir o iframe antigo pelo novo
            iframe.parentNode.replaceChild(newIframe, iframe);
        } else {
            row.style.display = 'none';
            row.style.opacity = '0';
            row.style.height = '0';
            
            // Limpar iframe se não estiver visível
            const iframe = row.querySelector('.radar-container iframe');
            if (iframe) {
                iframe.src = '';
            }
        }
    });
    
    // Atualizar controles de paginação
    atualizarPaginacao(totalJogos);
    
    // Fazer scroll para o topo da página
    window.scrollTo(0, 0);
}

function updateMatches() {
    const matchRows = document.querySelectorAll('.match-row');
    
    fetch('/get_matches')
        .then(response => response.json())
        .then(data => {
            // Atualizar contador de jogos
            const liveCount = document.querySelector('.live-count');
            if (liveCount) {
                liveCount.textContent = `(${data.matches.length})`;
            }

            console.log('Dados recebidos:', data);
            
            // Atualizar informações dos jogos
            data.matches.forEach(match => {
                console.log('Processando jogo:', match);
                console.log(`Placar recebido da API - Casa: ${match.score.home}, Visitante: ${match.score.away}`);
                const matchRow = document.querySelector(`[data-event-id="${match.id}"]`);
                console.log('Match row encontrada:', matchRow);
                if (matchRow) {
                    // Atualizar informações do jogo
                    matchRow.querySelector('.team.home img').src = match.homeTeam.logo;
                    matchRow.querySelector('.team.away img').src = match.awayTeam.logo;
                    
                    // Atualizar o placar usando os valores do score
                    const placar = `${match.score.home} - ${match.score.away}`;
                    console.log(`Atualizando placar do jogo ${match.id} para: ${placar} (Time: ${match.time})`);
                    matchRow.querySelector('.score').textContent = placar;
                    matchRow.querySelector('.match-time').textContent = match.time;
                    
                    // Atualizar iframe do radar e link
                    const radarContainer = matchRow.querySelector('.radar-container');
                    const iframe = radarContainer.querySelector('iframe');
                    const link = radarContainer.querySelector('a');
                    
                    // Só atualiza o radar se o jogo estiver na página atual
                    const isVisible = matchRow.style.display !== 'none';
                    if (isVisible) {
                        const widgetUrl = `https://widgets.sofascore.com/pt-BR/embed/attackMomentum?id=${match.id}&widgetTheme=light`;
                        console.log('URL do widget:', widgetUrl);
                        iframe.src = widgetUrl;
                        // Verificar se o widget carregou após atualizar a URL
                        checkWidget(iframe, match.id);
                    }
                    link.href = `https://www.sofascore.com/pt/match/${match.homeTeam.name.toLowerCase().replace(/\s+/g, '-')}-${match.awayTeam.name.toLowerCase().replace(/\s+/g, '-')}/${match.id}#id:${match.id}`;
                    link.textContent = `Placar ao vivo ${match.homeTeam.name} - ${match.awayTeam.name}`;
                }
            });
            
            // Reaplicar paginação após atualizar os dados
            mudarPagina(paginaAtual);
        })
        .catch(error => console.error('Erro ao atualizar dados:', error));
}

// Função para inicializar as atualizações
function initUpdates() {
    // Aplicar paginação inicial
    mudarPagina(1);
    
    // Primeira atualização após 1 segundo
    setTimeout(updateMatches, 1000);
    // Atualizar dados a cada 10 segundos para manter o placar mais preciso
    setInterval(updateMatches, 10000);
    
    // Log para monitorar as atualizações
    console.log('Sistema de atualização iniciado - intervalo: 10 segundos');
}

// Inicializar quando o documento estiver pronto
// Função para verificar se o widget carregou corretamente
function checkWidget(iframe, matchId) {
    console.log(`Verificando widget para jogo ${matchId}`);
    
    // Função para verificar o conteúdo do iframe
    const verifyContent = () => {
        try {
            // Tenta acessar o conteúdo do iframe
            const iframeContent = iframe.contentDocument || iframe.contentWindow.document;
            console.log(`Conteúdo do iframe para jogo ${matchId}:`, iframeContent.body.textContent);
            
            // Verifica diferentes condições de erro
            const content = iframeContent.body.textContent.toLowerCase();
            if (
                content.includes('404') || 
                content.includes('erro') ||
                content.includes('error') ||
                content.includes('not found') ||
                content.includes('não encontrad') ||
                !content.trim() ||
                content.includes('ocorreu um erro')
            ) {
                console.log(`Widget não disponível para jogo ${matchId}`);
                showError(matchId);
            }
        } catch (e) {
            // Se não conseguir acessar o conteúdo do iframe (por causa de CORS)
            console.log(`Erro ao verificar widget do jogo ${matchId}:`, e);
            // Tenta verificar pelo tamanho do iframe
            if (iframe.clientHeight < 50) {
                console.log(`Widget parece estar vazio para jogo ${matchId}`);
                showError(matchId);
            }
        }
    };

    // Primeira verificação após 2 segundos
    setTimeout(verifyContent, 2000);
    
    // Segunda verificação após 5 segundos para garantir
    setTimeout(verifyContent, 5000);
}

// Função para mostrar a mensagem de erro
function showError(matchId) {
    const iframe = document.querySelector(`#widget-container-${matchId} iframe`);
    const errorDiv = document.querySelector(`#error-${matchId}`);
    
    if (iframe && errorDiv) {
        iframe.style.display = 'none';
        errorDiv.style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', initUpdates);
