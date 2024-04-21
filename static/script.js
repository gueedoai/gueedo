document.addEventListener('DOMContentLoaded', function() {
  // Function to handle form submission
  function submitForm() {
    // Get the value of the input field with name="question"
    var questionValue = document.getElementById('user-input').value;

    // Log the captured question value for debugging
    console.log("Captured question value:", questionValue);

    // Append the user's question to the chatbox
    appendMessage('outgoing', questionValue);

    // Create a new XMLHttpRequest object
    var xhr = new XMLHttpRequest();

    // Define the request parameters
    xhr.open('POST', '/submit_question', true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    // Define the function to handle the response from the server
    xhr.onreadystatechange = function() {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status === 200) {
          // If the request is successful, handle the response
          var response = JSON.parse(xhr.responseText);
          console.log('Response from server:', response);
          // Append the server's response to the chatbox
          appendMessage('incoming', response.response);
        } else {
          // If there's an error, log it
          console.error('Error:', xhr.status);
        }
      }
    };

    // Create a JavaScript object with the question value
    var data = {
      question: questionValue
    };

    // Convert the JavaScript object to a JSON string
    var jsonData = JSON.stringify(data);

    // Send the JSON data to the server
    xhr.send(jsonData);

    // Clear the input field after sending the question
    document.getElementById('user-input').value = '';
  }

  // Function to append messages to the chatbox
  function appendMessage(type, message) {
    var chatbox = document.querySelector('.chatbox');
    var li = document.createElement('li');
    li.classList.add('chat', type);
    li.innerHTML = `<span class="material-symbols-outlined">smart_toy</span><p>${message}</p>`;
    chatbox.appendChild(li);
    // Scroll to the bottom of the chatbox to show the latest message
    chatbox.scrollTop = chatbox.scrollHeight;
  }

  // Attach an event listener to the form submission
  document.getElementById('input-form').addEventListener('submit', function(event) {
    // Prevent the default form submission behavior
    event.preventDefault();
    // Call the submitForm function to handle form submission
    submitForm();
  });

  // Attach an event listener to the send button
  document.getElementById('send-btn').addEventListener('click', function() {
    // Call the submitForm function when the send button is clicked
    submitForm();
  });

  // Toggle chatbot visibility
  var chatbotToggler = document.querySelector('.chatbot-toggler');
  var chatbot = document.querySelector('.chatbot');
  chatbotToggler.addEventListener('click', function() {
    document.body.classList.toggle('show-chatbot');
  });

  // Close chatbot
  var closeBtn = document.querySelector('.close-btn');
  closeBtn.addEventListener('click', function() {
    document.body.classList.remove('show-chatbot');
  });
});
