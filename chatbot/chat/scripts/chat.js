const http = new XMLHttpRequest();
const host = "http://localhost:8080/"

document.getElementById("user-input-submit").addEventListener("click", function(evt) {
	event.preventDefault();
	query();
});

/* Used for keeping the scroll-bar at the bottom of the chat window */
var scroll = document.getElementById("chat-window");

/*
 * Gets the user-input from form and clears it
 * @return {string} value - the user input
 */
function getUserInput() {
	var inputField = document.getElementById("user-input");
	var value = inputField.value;
	inputField.value = "";
	return value;
}

/*
 * Retrieves input from user-input field, adds the message to the chat window
 * and requests a response. Once the response is received, it is added to the
 * chat windows from the bot's user
 */
function query() {
	var input = getUserInput();

	// Don't do anything if the field is empty
	if (!input) { return; }

	populateChatWithMessage(input, "user")

	http.open("GET", host+"v2/response/"+input+"/", true);
  http.setRequestHeader("Content-Type", "text/plain");
	http.onreadystatechange = function() {
		if(this.readyState == 4 && this.status == 200) {
			var json = JSON.parse(http.responseText);
			var response = json.response;
			response = response.replace(/\n/g, '<br>');
			populateChatWithMessage(response, "bot");
		}
	}
  http.send();
	//var data = JSON.stringify({"queryResult": { "queryText": input }});
	//http.send(data);
}

/*
 * Populates the chat window with a new message from the specified role
 * @param {string} message - the chat message to be added
 * @param {string} role - bot/user, specifying who sent the messsage
 */
function populateChatWithMessage(message, role) {
	var msgDiv = createDiv(["msg", role]);
	var msgP = document.createElement("p");

	msgP.innerHTML = message;
	msgDiv.appendChild(msgP);

	var chatWindow = document.getElementById("chat-window");
	chatWindow.appendChild(msgDiv);

	// Keep scroll at the bottom
	scroll.scrollTop = scroll.scrollHeight - scroll.clientHeight;
}

/*
 * Creates div with classes
 * @param {list[{string}]} classes - list of classes
 * @return {object} div - returns the created div
 */
function createDiv(classes=[]) {
  var div = document.createElement("div");
  for (var i = 0; i<classes.length; i++) {
    div.classList.add(classes[i]);
  }
  return div;
}
