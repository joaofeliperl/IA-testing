# Use a imagem oficial do Python como base
FROM python:3.9

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos necessários para o container
COPY requirements.txt requirements.txt
COPY . .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta 5000 para a aplicação Flask
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "app.py"]
