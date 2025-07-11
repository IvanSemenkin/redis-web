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

function editMessage(button) {
  const messageDiv = button.closest('.message');
  const contentDiv = messageDiv.querySelector('.message-content');
  const messageId = messageDiv.dataset.id;
  const currentText = contentDiv.textContent;
  
  messageDiv.querySelector('.message-actions').style.display = 'none';
  
  const editorHtml = `
    <div class="message-editor">
      <textarea>${currentText}</textarea>
      <div class="message-editor-buttons">
        <button onclick="saveMessage(this, ${messageId})" class="btn-save">
          <i class="fas fa-save"></i> Сохранить
        </button>
        <button onclick="cancelEdit(this)" class="btn-cancel">
          <i class="fas fa-times"></i> Отмена
        </button>
      </div>
    </div>
  `;
  
  contentDiv.style.display = 'none';
  messageDiv.insertAdjacentHTML('beforeend', editorHtml);
}

function cancelEdit(button) {
  const messageDiv = button.closest('.message');
  messageDiv.querySelector('.message-content').style.display = '';
  messageDiv.querySelector('.message-actions').style.display = 'flex';
  messageDiv.querySelector('.message-editor').remove();
}

async function saveMessage(button, messageId) {
  const messageDiv = button.closest('.message');
  const newText = messageDiv.querySelector('.message-editor textarea').value;
  const userId = '{{ user_id }}'; // Или получите из URL
  
  try {
    const response = await fetch('/update_message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        message_id: messageId,
        new_content: newText
      })
    });
    
    if (response.ok) {
      messageDiv.querySelector('.message-content').textContent = newText;
      cancelEdit(button);
    } else {
      alert('Ошибка при сохранении');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Ошибка соединения');
  }
}

async function deleteMessage(button) {
  if (!confirm('Удалить это сообщение?')) return;
  
  const messageDiv = button.closest('.message');
  const messageId = messageDiv.dataset.id;
  const userId = '{{ user_id }}';
  
  try {
    const response = await fetch('/delete_message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        message_id: messageId
      })
    });
    
    if (response.ok) {
      messageDiv.remove();
    } else {
      alert('Ошибка при удалении');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Ошибка соединения');
  }
}