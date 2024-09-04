
let deleteProjectId = null;

function deleteProject(projectId) {
    deleteProjectId = projectId;
    $('#confirmModal').modal('show');
}

document.getElementById('confirmDeleteBtn').addEventListener('click', function () {
    if (deleteProjectId) {
        fetch(`/delete_project/${deleteProjectId}`, {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {  // Verifica se a resposta contém a chave 'message'
                    document.getElementById(`project-${deleteProjectId}`).remove();
                    $('#confirmModal').modal('hide');
                } else {
                    alert('Erro ao excluir o projeto');
                }
            })
            .catch(error => console.error('Erro:', error));
    }
});
