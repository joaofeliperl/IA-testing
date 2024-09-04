#!/bin/bash

# Ativar ambiente virtual, se não existir criar um
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Criar tabelas no banco de dados
python create_db.py

echo "Setup completo! Agora você pode rodar a aplicação com 'python app.py'."
