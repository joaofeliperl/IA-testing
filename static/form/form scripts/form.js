document.getElementById('fileUpload').addEventListener('click', function() {
    document.getElementById('fileInput').click();
});

document.getElementById('fileUpload').addEventListener('dragover', function(event) {
    event.preventDefault();
    this.style.borderColor = '#fff';
});

document.getElementById('fileUpload').addEventListener('dragleave', function() {
    this.style.borderColor = '#888';
});

document.getElementById('fileUpload').addEventListener('drop', function(event) {
    event.preventDefault();
    this.style.borderColor = '#888';
    let files = event.dataTransfer.files;
    handleFiles(files);
});

document.getElementById('fileInput').addEventListener('change', function(event) {
    let files = event.target.files;
    handleFiles(files);
});

function handleFiles(files) {
    const imagePreview = document.getElementById('imagePreview');
    let existingImages = imagePreview.children.length;

    if (existingImages >= 3) {
        alert("Você só pode adicionar até 3 imagens.");
        return;
    }

    for (let i = 0; i < files.length; i++) {
        if (existingImages >= 3) {
            alert("Você só pode adicionar até 3 imagens.");
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
            removeBtn.addEventListener('click', function() {
                imageContainer.remove();
            });

            imageContainer.appendChild(img);
            imageContainer.appendChild(removeBtn);
            imagePreview.appendChild(imageContainer);

            let reader = new FileReader();
            reader.onload = (function(aImg) {
                return function(e) {
                    aImg.src = e.target.result;
                };
            })(img);
            reader.readAsDataURL(file);

            existingImages++;
        } else {
            alert("Apenas imagens são permitidas.");
        }
    }
}
