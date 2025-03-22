# Time - Sistema de Gerenciamento de Ponto Eletrônico

Este é um sistema de gerenciamento de ponto eletrônico desenvolvido em Python utilizando o framework Flask. O sistema permite gerenciar registros de entrada e saída de funcionários, filtrando os dados por funcionário e evento, e oferecendo uma interface simples e funcional.

> **Aviso**: O frontend do sistema está em reformulação. Por enquanto, somente a API está funcionando. Utilize ferramentas como Postman ou Insomnia para consumir a API.

## 🚀 Funcionalidades

- **Cadastro de Pontos**: Registre horários de entrada e saída, associados a funcionários e eventos específicos.
- **Relatório de Pontos**: Exiba e filtre os registros por:
  - Funcionário (nome ou matrícula);
  - Evento (código ou descrição);
  - Combinação de ambos os critérios.
- **Autenticação**: Sistema protegido com autenticação de usuários.

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python com Flask
- **Banco de Dados**: SQLite
- **Frontend**: HTML, CSS e Jinja2
- **Autenticação**: Flask-Login

## ⚙️ Como Instalar e Executar

### Pré-requisitos

- Python 3.10 ou superior
- Ambiente virtual (`virtualenv` ou `venv`)
- SQLite (já integrado ao Python)

### Passos para Execução

1. **Clonar o repositório:**

   ```bash
   git clone https://github.com/seu-usuario/nome-do-repositorio.git
   cd nome-do-repositorio

Criar e ativar o ambiente virtual:

Para criar o ambiente virtual:
```json
python -m venv venv
```

2. **Para ativar o ambiente virtual:**

No Windows:
```json
.\venv\Scripts\activate
```

No Linux ou macOS:
```json
source venv/bin/activate
```

3. **Instalar as dependências:**
```json
pip install -r requirements.txt
```

4. **Executar o projeto:**

Para rodar o projeto, basta executar o arquivo app.py:
```json
python app.py
```

