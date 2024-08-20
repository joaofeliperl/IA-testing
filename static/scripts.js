document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const imageContainer = document.getElementById('imageContainer');
    const noImages = document.getElementById('noImages');

    // Highlight the drop zone when a file is dragged over it
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    // Remove highlight when the file is dragged away
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    // Handle file drop
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    // Handle file selection through input
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        handleFiles(fileInput.files);
    });

    function handleFiles(files) {
        let hasImages = false;

        for (const file of files) {
            if (file.type.startsWith('image/')) {
                hasImages = true;
                const reader = new FileReader();
                reader.onload = (e) => {
                    const imageElement = document.createElement('div');
                    imageElement.classList.add('imagePreview');
                    imageElement.style.backgroundImage = `url(${e.target.result})`;

                    const deleteButton = document.createElement('button');
                    deleteButton.classList.add('deleteButton');
                    deleteButton.innerText = '×';
                    deleteButton.addEventListener('click', () => {
                        imageContainer.removeChild(imageElement);
                        updateNoImagesVisibility();
                    });

                    imageElement.appendChild(deleteButton);
                    imageContainer.appendChild(imageElement);

                    // Ensure the container is displayed
                    imageContainer.style.display = 'flex';
                };
                reader.readAsDataURL(file);
            }
        }

        // Update visibility of noImages
        updateNoImagesVisibility();
    }

    function updateNoImagesVisibility() {
        if (imageContainer.children.length > 0) {
            noImages.style.display = 'none';
        } else {
            noImages.style.display = 'flex';
        }
    }

    // Initial check to set correct visibility of noImages
    updateNoImagesVisibility();
});
