// document.getElementById('menu-button').addEventListener('click', function() {
//     const menu = document.getElementById('menu');
//     menu.style.display = menu.style.display === 'none' || menu.style.display === '' ? 'block' : 'none';
// });

const menuButtonCadastro = document.getElementById('menu-button-cadastro');
const menuButtonRelatorio = document.getElementById('menu-button-relatorio');
const menu = document.getElementById('menu');
const menuRelatorio = document.getElementById('menu-relatorio');

function toggleMenu(event) {
    event.stopPropagation();
    // Oculta o menu de relatório se ele estiver visível
    if (menuRelatorio.style.display === 'block') {
        menuRelatorio.style.display = 'none';
    }

    // Mostra o menu de cadastro
    const rect = menuButtonCadastro.getBoundingClientRect(); // Posição do botão Cadastro
    menu.style.left = `${rect.left}px`;
    menu.style.top = `${rect.bottom + window.scrollY}px`; // Adiciona a posição do botão ao topo
    menu.style.display = 'block'; // Mostra o menu de cadastro
}

function toggleMenuRelatorio(event) {
    event.stopPropagation();
    // Oculta o menu de cadastro se ele estiver visível
    if (menu.style.display === 'block') {
        menu.style.display = 'none';
    }

    // Mostra o menu de relatório
    const rect = menuButtonRelatorio.getBoundingClientRect(); // Posição do botão Relatório
    menuRelatorio.style.left = `${rect.left}px`;
    menuRelatorio.style.top = `${rect.bottom + window.scrollY}px`; // Adiciona a posição do botão ao topo
    menuRelatorio.style.display = 'block'; // Mostra o menu de relatório
}

menuButtonCadastro.addEventListener('click', toggleMenu);
menuButtonRelatorio.addEventListener('click', toggleMenuRelatorio);

// Fecha os menus ao clicar em qualquer lugar fora deles
document.addEventListener('click', function(event) {
    if (menu.style.display === 'block') {
        menu.style.display = 'none';
    }
    if (menuRelatorio.style.display === 'block') {
        menuRelatorio.style.display = 'none';
    }
});

// Fecha o menu de cadastro ao clicar em um link
menu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', function() {
        menu.style.display = 'none'; // Fecha o menu de cadastro ao clicar em um link
    });
});

// Fecha o menu de relatório ao clicar em um link
menuRelatorio.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', function() {
        menuRelatorio.style.display = 'none'; // Fecha o menu de relatório ao clicar em um link
    });
});

document.getElementById('endereco').addEventListener('focus', function() {
    // Limpa a lista antes de buscar os endereços
    const enderecosList = document.getElementById('enderecos-list');
    enderecosList.innerHTML = '';

    fetch('/enderecos')
        .then(response => response.json())
        .then(enderecos => {
            enderecos.forEach(endereco => {
                const li = document.createElement('li');
                li.textContent = endereco.rua;
                li.dataset.id = endereco.id;  // Armazena o ID do endereço
                li.addEventListener('click', function() {
                    document.getElementById('endereco').value = endereco.rua;  // Preenche o campo de entrada
                    enderecosList.style.display = 'none';  // Oculta a lista
                });
                enderecosList.appendChild(li);
            });

            if (enderecos.length > 0) {
                enderecosList.style.display = 'block';  // Mostra a lista se houver endereços
            }
        })
        .catch(error => console.error('Erro ao buscar endereços:', error));
});

// Fecha a lista ao clicar fora dela
document.addEventListener('click', function(event) {
    const enderecosList = document.getElementById('enderecos-list');
    if (!enderecosList.contains(event.target) && event.target.id !== 'endereco') {
        enderecosList.style.display = 'none';
    }
});
