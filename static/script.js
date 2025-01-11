$(document).ready(function () {
	// Chat UI Elements
	const chatIcon = $('#chatIcon');
	const chatContainer = $('#chatContainer');
	const minimizeChat = $('#minimizeChat');
	const userInput = $('#userInput');
	const sendMessage = $('#sendMessage');
	const chatMessages = $('#chatMessages');

	// Toggle chat container
	chatIcon.click(function () {
		chatContainer.toggleClass('show');
	});

	// Minimize chat
	minimizeChat.click(function () {
		chatContainer.removeClass('show');
	});

	// Format message text
	function formatMessage(text) {
		// Replace numbered lists (e.g., "1.", "2.", etc)
		text = text.replace(/(\d+\.\s+)/g, '<br>$1');

		// Replace bullet points
		text = text.replace(/([•\-]\s+)/g, '<br>$1');

		// Replace multiple consecutive spaces with a single space
		text = text.replace(/\s{2,}/g, ' ');

		// Replace ":" followed by text with ": " and a line break
		text = text.replace(/:\s*([A-Za-z])/g, ':<br>$1');

		// Remove line break if it's at the start of the text
		text = text.replace(/^<br>/, '');

		return text;
	}

	// Send message function
	function sendUserMessage() {
		const message = userInput.val().trim();
		if (message) {
			// Add user message to chat
			appendMessage('user', message);
			userInput.val('');

			// Send message to backend
			$.ajax({
				url: '/api/chat',
				method: 'POST',
				contentType: 'application/json',
				data: JSON.stringify({ message: message }),
				success: function (response) {
					appendMessage('bot', response.reply);
				},
				error: function (error) {
					console.error('Error:', error);
					appendMessage(
						'bot',
						'Maaf, terjadi kesalahan. Silakan coba lagi nanti.'
					);
				},
			});
		}
	}

	// Append message to chat
	function appendMessage(sender, message) {
		const wrapper = $('<div></div>').addClass('message-wrapper');
		const messageDiv = $('<div></div>')
			.addClass('message')
			.addClass(sender === 'user' ? 'user-message' : 'bot-message')
			.text(message);

		wrapper.append(messageDiv);
		const chatMessages = $('#chatMessages');
		chatMessages.append(wrapper);

		// Scroll otomatis ke bawah
		chatMessages.scrollTop = chatMessages.scrollHeight;
	}

	// Event listeners
	sendMessage.click(sendUserMessage);

	userInput.on('keydown', function (e) {
		if (e.key === 'Enter') {
			sendUserMessage();
		}
	});

	// Initial greeting
	setTimeout(function () {
		appendMessage(
			'bot',
			'Halo! Saya adalah asisten kampus Anda. Ada yang bisa saya bantu?'
		);
	}, 500);
});
