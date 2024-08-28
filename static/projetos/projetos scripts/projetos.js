
let deleteProjectId = null;

function deleteProject(projectId) {
    deleteProjectId = projectId;
    $('#confirmModal').modal('show');
}

document.getElementById('confirmDeleteBtn').addEventListener('click', function() {
    if (deleteProjectId) {
        // Substitua a URL pelo endpoint de exclusão do projeto
        fetch(`/delete_project/${deleteProjectId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`project-${deleteProjectId}`).remove();
                $('#confirmModal').modal('hide');
            } else {
                alert('Erro ao excluir o projeto');
            }
        })
        .catch(error => console.error('Erro:', error));
    }
});
