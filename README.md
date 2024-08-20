# Test Case Generator

Este é um projeto de exemplo desenvolvido com Flask para gerar casos de teste automaticamente a partir de uma captura de tela e uma descrição fornecida pelo usuário. O objetivo é auxiliar testadores de software a criarem casos de teste de forma rápida e eficiente, utilizando um sistema baseado em IA.

## Objetivo do Projeto

O **Test Case Generator** foi criado para ajudar profissionais de QA (Quality Assurance) e testadores de software a automatizar a geração de casos de teste. O usuário pode enviar uma imagem (screenshot) de uma interface de usuário e uma descrição da tela, e o sistema gera uma lista de casos de teste sugeridos que podem ser usados para validar os elementos da interface.

## Funcionalidades

- **Upload de Screenshot:** O usuário pode fazer upload de uma imagem da interface de um aplicativo ou website.
- **Descrição da Tela:** O usuário pode fornecer uma descrição da funcionalidade ou dos elementos presentes na tela.
- **Geração de Casos de Teste:** Com base na imagem e na descrição, o sistema gera uma lista de casos de teste sugeridos.

## Como Rodar o Projeto Localmente

### Pré-requisitos

Certifique-se de ter o Python 3.x instalado em sua máquina. Você pode verificar se o Python está instalado executando:

```bash
python --version


### Passos para Configuração

1. **Clone o repositório:**

   Clone o repositório do projeto para o seu ambiente local:

   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio


2. **Crie um ambiente virtual [opcional, mas recomendado] **

    python -m venv venv
    source venv/bin/activate  # No Windows use `venv\Scripts\activate`

3. **Instale as dependências:**
    pip install -r requirements.txt


4. **Execute a aplicação:**
    python app.py


5. **Acesse a aplicação:**
    Abra o navegador e vá para http://127.0.0.1:5000/ para acessar a aplicação.
