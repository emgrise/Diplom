function loadModal() {
    // Получаем iframe
    const modalFrame = document.getElementById('modalFrame');
    if (!modalFrame) return;

    // Запрашиваем генерацию нового модального окна
    fetch('/generate_modal')
        .then(response => response.json())
        .then(data => {
            // Устанавливаем src для iframe
            modalFrame.src = data.path;
        })
        .catch(error => {
            console.error('Error loading modal:', error);
        });
}

// Функция для обновления модального окна
function refreshModal() {
    loadModal();
}

// Загружаем модальное окно при загрузке страницы
document.addEventListener('DOMContentLoaded', loadModal); 