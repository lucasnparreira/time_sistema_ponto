document.getElementById('menu-button').addEventListener('click', function() {
    const menu = document.getElementById('menu');
    menu.style.display = menu.style.display === 'none' || menu.style.display === '' ? 'block' : 'none';
});

// Busca funcionário por matrícula e preenche o formulário
document.getElementById('buscar-funcionario').addEventListener('click', function() {
    const matricula = document.getElementById('matricula').value;

    if (!matricula) {
        alert('Por favor, insira a matrícula.');
        return;
    }

    fetch(`/funcionario/${matricula}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
        } else {
            document.getElementById('nome').value = data.nome;
            document.getElementById('funcao').value = data.funcao;
            document.getElementById('data_inicio').value = data.data_inicio;
            document.getElementById('data_termino').value = data.data_termino || '';
            document.getElementById('departamento').value = data.departamento;
            document.getElementById('gerente').value = data.gerente;
            document.getElementById('endereco').value = data.endereco;
            document.getElementById('telefone').value = data.telefone;
            document.getElementById('cpf').value = data.cpf;
            document.getElementById('rg').value = data.rg;
            document.getElementById('banco').value = data.banco;
            document.getElementById('agencia').value = data.agencia;
            document.getElementById('conta_corrente').value = data.conta_corrente;
        }
    })
    .catch(error => console.error('Error:', error));
});

// Adiciona um novo funcionário
document.getElementById('funcionario-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());

    fetch('/funcionario', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        event.target.reset();
    })
    .catch(error => console.error('Error:', error));
});

// Atualiza os dados do funcionário
document.getElementById('atualizar-funcionario').addEventListener('click', function() {
    const formData = new FormData(document.getElementById('funcionario-form'));
    const data = Object.fromEntries(formData.entries());
    const matricula = data.matricula;

    if (!matricula) {
        alert('Por favor, insira a matrícula.');
        return;
    }

    fetch(`/funcionario/${matricula}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => console.error('Error:', error));
});


// tela de index.html
// Abre ou fecha o menu ao clicar no botão
document.getElementById('menu-button').addEventListener('click', function(event) {
    const menu = document.getElementById('menu');
    menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
    event.stopPropagation(); // Evita que o clique no botão feche o menu imediatamente
});

// Fecha o menu ao clicar fora dele
document.addEventListener('click', function(event) {
    const menu = document.getElementById('menu');
    if (menu.style.display === 'block') {
        menu.style.display = 'none';
    }
});

// Fecha o menu ao clicar em qualquer link
document.querySelectorAll('#menu a').forEach(link => {
    link.addEventListener('click', function() {
        const menu = document.getElementById('menu');
        menu.style.display = 'none';
    });
});
