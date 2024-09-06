let deleteProjectId = null;
const maxProjects = 9;

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
                if (data.message) {
                    document.getElementById(`project-${deleteProjectId}`).remove();
                    $('#confirmModal').modal('hide');
                } else {
                    alert('Erro ao excluir o projeto');
                }
            })
            .catch(error => console.error('Erro:', error));
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const projectCount = document.querySelectorAll('.gray-card').length;
    const newProjectBtn = document.getElementById('new-project-btn');

    if (projectCount >= maxProjects) {
        newProjectBtn.disabled = true;
        newProjectBtn.title = "You have already reached the maximum number of projects";
    }
});
