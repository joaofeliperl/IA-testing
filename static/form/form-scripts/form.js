// Ativa o upload de arquivos ao clicar na área de arrastar e soltar
document.getElementById('fileUpload').addEventListener('click', function () {
    document.getElementById('fileInput').click();
});

// Altera a borda ao arrastar arquivos sobre a área
document.getElementById('fileUpload').addEventListener('dragover', function (event) {
    event.preventDefault();
    this.style.borderColor = '#fff';
});

// Retorna a borda ao estado original ao sair da área
document.getElementById('fileUpload').addEventListener('dragleave', function () {
    this.style.borderColor = '#888';
});

// Manipula arquivos soltos na área
document.getElementById('fileUpload').addEventListener('drop', function (event) {
    event.preventDefault();
    this.style.borderColor = '#888';
    let files = event.dataTransfer.files;
    handleFiles(files);
});

// Detecta mudança no input de arquivo
document.getElementById('fileInput').addEventListener('change', function (event) {
    let files = event.target.files;
    handleFiles(files);
});

// Função principal para manipular o upload de arquivos
function handleFiles(files) {
    const imagePreview = document.getElementById('imagePreview');
    let existingImages = imagePreview.children.length;

    if (existingImages >= 3) {
        displayMessage("Você só pode adicionar até 3 imagens.", "warning");
        return;
    }

    for (let i = 0; i < files.length; i++) {
        if (existingImages >= 3) {
            displayMessage("Você só pode adicionar até 3 imagens.", "warning");
            break;
        }

        let file = files[i];

        if (file.type.startsWith('image/')) {
            let imageContainer = document.createElement('div');
            imageContainer.classList.add('image-container');

            let img = document.createElement("img");
            img.classList.add("uploaded-image");
            img.file = file;

            let removeBtn = document.createElement("button");
            removeBtn.classList.add("remove-btn");
            removeBtn.innerHTML = "&times;";

            // Função de remoção
            removeBtn.addEventListener('click', function () {
                imageContainer.remove();
                updateImageCount();
            });

            imageContainer.appendChild(img);
            imageContainer.appendChild(removeBtn);
            imagePreview.appendChild(imageContainer);

            let reader = new FileReader();
            reader.onload = (function (aImg) {
                return function (e) {
                    aImg.src = e.target.result;
                };
            })(img);
            reader.readAsDataURL(file);

            existingImages++;
        } else {
            displayMessage("Apenas imagens são permitidas.", "error");
        }
    }
    updateImageCount();
}

// Função para atualizar a contagem de imagens e exibir uma mensagem
function updateImageCount() {
    const imagePreview = document.getElementById('imagePreview');
    let existingImages = imagePreview.children.length;

    if (existingImages < 3) {
        displayMessage(`Você pode adicionar mais ${3 - existingImages} imagens.`, "info");
    }
}

// Função para exibir mensagens na tela (evitando alerts)
function displayMessage(message, type) {
    const messageContainer = document.createElement('div');
    messageContainer.className = `alert alert-${type}`;
    messageContainer.textContent = message;

    // Adiciona a mensagem ao body ou à área desejada
    document.body.appendChild(messageContainer);

    // Remove a mensagem após 3 segundos
    setTimeout(function () {
        messageContainer.remove();
    }, 3000);
}
