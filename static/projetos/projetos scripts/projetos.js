let projectIdToDelete = null;

function deleteProject(projectId) {
    projectIdToDelete = projectId; // Salva o ID do projeto a ser excluído
    $('#confirmModal').modal('show'); // Exibe o modal de confirmação
}

document.getElementById('confirmDeleteBtn').addEventListener('click', function() {
    if (projectIdToDelete !== null) {
        fetch(`/delete_project/${projectIdToDelete}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message); // Mostrar mensagem de sucesso
                document.querySelector(`#project-${projectIdToDelete}`).remove(); // Remover o projeto da interface
            } else if (data.error) {
                alert(data.error); // Mostrar mensagem de erro
            }
        })
        .catch(error => console.error('Error:', error))
        .finally(() => {
            $('#confirmModal').modal('hide'); // Oculta o modal de confirmação após a ação
            projectIdToDelete = null; // Limpa o ID do projeto a ser excluído
        });
    }
});
