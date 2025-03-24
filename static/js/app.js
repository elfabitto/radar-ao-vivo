// Configurações de paginação
const JOGOS_POR_PAGINA = 10;
let paginaAtual = 1;
let abaAtual = 'todos';

// Objeto para armazenar os placares anteriores
const placaresAnteriores = {};

// Array para armazenar os IDs dos jogos favoritos
let favoritos = [];

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
    // Selecionar container ativo
    const containerAtivo = document.getElementById(`${abaAtual}-container`);
    if (!containerAtivo) return;
    
    const matchRows = containerAtivo.querySelectorAll('.match-row');
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
        } else {
            row.style.display = 'none';
            row.style.opacity = '0';
            row.style.height = '0';
        }
    });
    
    // Atualizar controles de paginação
    atualizarPaginacao(totalJogos);
    
    // Fazer scroll para o topo da página
    window.scrollTo(0, 0);
}

function updateMatches() {
    const matchRows = document.querySelectorAll('#todos-container .match-row');
    
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
                const matchId = match.id;
                
                // Verificar se o jogo já existe
                let matchRow = document.querySelector(`#todos-container [data-event-id="${matchId}"]`);
                
                if (matchRow) {
                    // Atualizar informações do jogo existente
                    matchRow.querySelector('.team.home img').src = match.homeTeam.logo;
                    matchRow.querySelector('.team.away img').src = match.awayTeam.logo;
                    
                    // Atualizar o placar
                    const homeScoreEl = matchRow.querySelector('.team-score-container:first-child .score');
                    const awayScoreEl = matchRow.querySelector('.team-score-container:last-child .score');
                    
                    homeScoreEl.textContent = match.homeTeam.score;
                    awayScoreEl.textContent = match.awayTeam.score;
                    
                    matchRow.querySelector('.match-time').textContent = match.time;
                    
                    // Atualizar link sem mexer no iframe
                    const radarContainer = matchRow.querySelector('.radar-container');
                    const link = radarContainer.querySelector('a');
                    
                    link.href = `https://www.sofascore.com/pt/match/${match.homeTeam.name.toLowerCase().replace(/\s+/g, '-')}-${match.awayTeam.name.toLowerCase().replace(/\s+/g, '-')}/${matchId}#id:${matchId}`;
                    link.textContent = `Placar ao vivo ${match.homeTeam.name} - ${match.awayTeam.name}`;
                    
                    // Atualizar também no container de favoritos se existir
                    const favMatchRow = document.querySelector(`#favoritos-container [data-event-id="${matchId}"]`);
                    if (favMatchRow) {
                        favMatchRow.querySelector('.team.home img').src = match.homeTeam.logo;
                        favMatchRow.querySelector('.team.away img').src = match.awayTeam.logo;
                        
                        favMatchRow.querySelector('.team-score-container:first-child .score').textContent = match.homeTeam.score;
                        favMatchRow.querySelector('.team-score-container:last-child .score').textContent = match.awayTeam.score;
                        
                        favMatchRow.querySelector('.match-time').textContent = match.time;
                    }
                }
            });
            
            // Verificar se algum jogo favorito foi removido da lista de jogos ao vivo
            if (abaAtual === 'favoritos') {
                atualizarContainerFavoritos(true);
            }
        })
        .catch(error => console.error('Erro ao atualizar dados:', error));
}

// Função para inicializar as atualizações
function initUpdates() {
    // Carregar favoritos do localStorage
    carregarFavoritos();
    
    // Configurar eventos das abas
    configurarAbas();
    
    // Configurar eventos dos botões de favorito
    configurarBotoesFavorito();
    
    // Aplicar paginação inicial
    mudarPagina(1);
    
    // Primeira atualização após 1 segundo
    setTimeout(updateMatches, 1000);
    // Atualizar dados a cada 60 segundos para manter o placar mais preciso
    // Aumentado o intervalo para evitar atualizações frequentes que podem afetar os widgets
    setInterval(updateMatches, 60000);
    
    // Log para monitorar as atualizações
    console.log('Sistema de atualização iniciado - intervalo: 60 segundos');
}

// Função para carregar favoritos do localStorage
function carregarFavoritos() {
    const favoritosStorage = localStorage.getItem('jogos_favoritos');
    if (favoritosStorage) {
        favoritos = JSON.parse(favoritosStorage);
        console.log('Favoritos carregados:', favoritos);
        
        // Atualizar contagem de favoritos
        atualizarContadorFavoritos();
        
        // Marcar botões de favoritos como ativos
        favoritos.forEach(id => {
            const btn = document.querySelector(`.favorito-btn[data-id="${id}"]`);
            if (btn) {
                btn.classList.add('ativo');
                btn.title = 'Remover dos favoritos';
            }
        });
    }
}

// Função para salvar favoritos no localStorage
function salvarFavoritos() {
    localStorage.setItem('jogos_favoritos', JSON.stringify(favoritos));
    console.log('Favoritos salvos:', favoritos);
}

// Função para configurar eventos das abas
function configurarAbas() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.getAttribute('data-tab');
            mudarAba(tabId);
        });
    });
}

// Função para mudar de aba
function mudarAba(novaAba) {
    if (novaAba === abaAtual) return;
    
    // Atualizar aba ativa
    abaAtual = novaAba;
    
    // Atualizar classes das abas
    document.querySelectorAll('.tab').forEach(tab => {
        if (tab.getAttribute('data-tab') === abaAtual) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Mostrar/esconder containers
    if (abaAtual === 'todos') {
        document.getElementById('todos-container').style.display = 'flex';
        document.getElementById('favoritos-container').style.display = 'none';
    } else {
        document.getElementById('todos-container').style.display = 'none';
        document.getElementById('favoritos-container').style.display = 'flex';
        
        // Atualizar container de favoritos sem recriar os widgets
        atualizarContainerFavoritos(true);
    }
    
    // Resetar paginação
    paginaAtual = 1;
    atualizarPaginacao(abaAtual === 'todos' ? 
        document.querySelectorAll('#todos-container .match-row').length : 
        favoritos.length);
}

// Função para configurar eventos dos botões de favorito
function configurarBotoesFavorito() {
    document.querySelectorAll('.favorito-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const id = btn.getAttribute('data-id');
            toggleFavorito(id, btn);
        });
    });
}

// Função para alternar favorito
function toggleFavorito(id, btn) {
    const index = favoritos.indexOf(id);
    
    if (index === -1) {
        // Adicionar aos favoritos
        favoritos.push(id);
        btn.classList.add('ativo');
        btn.title = 'Remover dos favoritos';
    } else {
        // Remover dos favoritos
        favoritos.splice(index, 1);
        btn.classList.remove('ativo');
        btn.title = 'Adicionar aos favoritos';
        
        // Se estiver na aba de favoritos, atualizar a visualização
        if (abaAtual === 'favoritos') {
            atualizarContainerFavoritos(true);
        }
    }
    
    // Salvar favoritos no localStorage
    salvarFavoritos();
    
    // Atualizar contagem de favoritos
    atualizarContadorFavoritos();
}

// Função para atualizar o contador de favoritos
function atualizarContadorFavoritos() {
    const contador = document.querySelector('.favoritos-count');
    if (contador) {
        contador.textContent = `(${favoritos.length})`;
    }
}

// Função para atualizar o container de favoritos
function atualizarContainerFavoritos(preservarWidgets = false) {
    const container = document.getElementById('favoritos-container');
    const semFavoritos = container.querySelector('.sem-favoritos');
    
    // Verificar se há favoritos
    if (favoritos.length === 0) {
        // Mostrar mensagem de sem favoritos
        semFavoritos.style.display = 'block';
        
        // Remover jogos existentes
        container.querySelectorAll('.match-row').forEach(row => {
            row.remove();
        });
        
        return;
    }
    
    // Esconder mensagem de sem favoritos
    semFavoritos.style.display = 'none';
    
    // Obter jogos existentes no container de favoritos
    const jogosExistentes = {};
    container.querySelectorAll('.match-row').forEach(row => {
        const id = row.getAttribute('data-event-id');
        if (!favoritos.includes(id)) {
            // Remover jogos que não estão mais nos favoritos
            row.remove();
        } else {
            // Manter jogos que ainda estão nos favoritos
            jogosExistentes[id] = row;
        }
    });
    
    // Adicionar jogos favoritos que ainda não existem no container
    favoritos.forEach(id => {
        // Verificar se o jogo já existe no container de favoritos
        if (!jogosExistentes[id]) {
            const jogoOriginal = document.querySelector(`#todos-container .match-row[data-event-id="${id}"]`);
            if (jogoOriginal) {
                // Clonar o jogo original
                const jogoClone = jogoOriginal.cloneNode(true);
                
                // Atualizar botão de favorito no clone
                const btnFavorito = jogoClone.querySelector('.favorito-btn');
                btnFavorito.classList.add('ativo');
                btnFavorito.title = 'Remover dos favoritos';
                
                // Adicionar evento ao botão de favorito no clone
                btnFavorito.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    const id = btnFavorito.getAttribute('data-id');
                    
                    // Remover dos favoritos
                    const index = favoritos.indexOf(id);
                    if (index !== -1) {
                        favoritos.splice(index, 1);
                    }
                    
                    // Atualizar botão original
                    const btnOriginal = document.querySelector(`#todos-container .favorito-btn[data-id="${id}"]`);
                    if (btnOriginal) {
                        btnOriginal.classList.remove('ativo');
                        btnOriginal.title = 'Adicionar aos favoritos';
                    }
                    
                    // Salvar favoritos
                    salvarFavoritos();
                    
                    // Atualizar contagem
                    atualizarContadorFavoritos();
                    
                    // Atualizar container
                    atualizarContainerFavoritos(true);
                });
                
                // Preservar o iframe original para evitar recarregamento
                if (preservarWidgets) {
                    const iframeOriginal = jogoOriginal.querySelector('.radar-container iframe');
                    const iframeClone = jogoClone.querySelector('.radar-container iframe');
                    
                    if (iframeOriginal && iframeOriginal.src && iframeOriginal.src !== 'about:blank') {
                        iframeClone.src = iframeOriginal.src;
                    }
                }
                
                // Adicionar ao container de favoritos
                container.insertBefore(jogoClone, semFavoritos);
            }
        }
    });
    
    // Atualizar paginação
    atualizarPaginacao(favoritos.length);
}

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
