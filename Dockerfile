# Use a imagem oficial do Python como base
FROM python:3.9

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Instalar o Tesseract OCR
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev

# Copiar os arquivos necessários para o container
COPY requirements.txt requirements.txt
COPY . .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta 5000 para a aplicação Flask
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "app.py"]
