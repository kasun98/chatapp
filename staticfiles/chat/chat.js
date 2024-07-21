document.addEventListener('DOMContentLoaded', function() {
    
    


});



function createMessageElement(message, isSentByCurrentUser) {
    // Common elements
    const messageContainer = document.createElement('div');
    

    if (isSentByCurrentUser) {
        // Message sent by current user
        messageContainer.className = 'message-sent';
        const senderInfo = `
            <div class="d-flex align-items-center mb-2" style="justify-content: end;">
                <div>
                    <div class="font-weight-bold" style="text-align:end; padding-right: 5px;">You</div>
                    <div class="text-muted small" style="text-align: end; padding-right: 5px;">${message.timestamp}</div>
                </div>
                <img src="https://via.placeholder.com/40" class="rounded-circle mr-2" alt="User">
            </div>
            <div  class="message-content-sent bg-light p-2 rounded">
                ${message.message}
            </div>
        `;
        messageContainer.innerHTML = senderInfo;
    } else {
        // Message received from others
        messageContainer.className = 'message';
        const senderInfo = `
            <div class="d-flex align-items-center mb-2">
                <img src="https://via.placeholder.com/40" class="rounded-circle mr-2" alt="User">
                <div>
                    <div class="font-weight-bold">${message.sender}</div>
                    <div class="text-muted small">${message.timestamp}</div>
                </div>
            </div>
            <div  class="message-content bg-light p-2 rounded">
                ${message.message}
            </div>
        `;
        messageContainer.innerHTML = senderInfo;
    }

   
    return messageContainer;
}

function hello(id) {
    const userElement = document.getElementById('user_name');
    const currentUser = userElement.getAttribute('data-username');

    document.querySelector('#category').innerHTML = '';
    document.querySelector('#members').innerHTML = '';
    const chatbox = document.getElementById('chatbox');
    
    // Remove all children elements with class 'message' or 'message-sent'
    while (chatbox.firstChild) {
        chatbox.removeChild(chatbox.firstChild);
    }
    
    fetch(`/room/${id}`)
    .then(response => response.json())
    .then(data => {
        // Print data
        console.log(data);

        const category = document.querySelector('#category').innerHTML = data.room_name;
        const members = document.querySelector('#members').innerHTML = (data.members.length + 1);

        // Loop through each message and append to the chatbox
        data.messages.forEach(message => {
            const isSentByCurrentUser = message.sender === currentUser;
            const messageElement = createMessageElement(message, isSentByCurrentUser);
            chatbox.appendChild(messageElement);
        });

        // Scroll chatbox to the latest message
        chatbox.scrollTop = chatbox.scrollHeight;
    
 
        
    })
    .catch(error => console.error('Error fetching messages:', error));
}
