document.addEventListener('DOMContentLoaded', function() {
    // Добавляем обработчики для всех карточек
    const cards = document.querySelectorAll('.user-card');
    
    cards.forEach(card => {
        // Эффект при наведении
        card.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
        });
        
        // Можно кликнуть в любом месте карточки
        card.addEventListener('click', function() {
            const link = this.getAttribute('data-href');
            if (link) {
                window.location.href = link;
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Обработчики для кнопок удаления
    const deleteButtons = document.querySelectorAll('.btn-delete');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить этот диалог? Это действие нельзя отменить.')) {
                e.preventDefault();
            }
        });
    });
});