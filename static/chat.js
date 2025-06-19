(function() {
  const script = document.currentScript;
  const customerId = script.dataset.id || '';

  const button = document.createElement('div');
  button.id = 'chat-button';
  button.textContent = '💬';
  document.body.appendChild(button);

  const chatWindow = document.createElement('div');
  chatWindow.id = 'chat-window';
  chatWindow.innerHTML = '<div id="chat-messages"></div><input id="chat-input" placeholder="Type a message" />';
  document.body.appendChild(chatWindow);
  chatWindow.style.display = 'none';

  button.addEventListener('click', () => {
    chatWindow.style.display = chatWindow.style.display === 'none' ? 'block' : 'none';
  });

  const input = chatWindow.querySelector('#chat-input');
  const messagesDiv = chatWindow.querySelector('#chat-messages');

  function addMessage(text, cls) {
    const div = document.createElement('div');
    div.className = cls;
    div.textContent = text;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  input.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && this.value.trim() !== '') {
      const msg = this.value.trim();
      addMessage(msg, 'user');
      this.value = '';
      fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: msg, customer_id: customerId})
      })
      .then(r => r.json())
      .then(d => {
        if (d.reply) addMessage(d.reply, 'bot');
        else if (d.error) addMessage('Error: ' + d.error, 'error');
      })
      .catch(err => {
        addMessage('Error: ' + err, 'error');
      });
    }
  });
})();
