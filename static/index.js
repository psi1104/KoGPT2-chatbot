var sendForm = document.querySelector("#chatform"),
	textInput = document.querySelector(".chatbox"),
	chatList = document.querySelector(".chatlist"),
	userBubble = document.querySelectorAll(".userInput")

sendForm.onkeydown = function (e) {
	if (e.keyCode == 13) {
		e.preventDefault();

		//No mix ups with upper and lowercases
		var input = textInput.value.toLowerCase();

		//Empty textarea fix
		if (input.length > 0) {
			createBubble(input);
		}
	}
};

sendForm.addEventListener("submit", function (e) {
	//so form doesnt submit page (no page refresh)
	e.preventDefault();

	//No mix ups with upper and lowercases
	var input = textInput.value.toLowerCase();

	//Empty textarea fix
	if (input.length > 0) {
		createBubble(input);
	}
}); //end of eventlistener

var createBubble = function (input) {
	//create input bubble
	var chatBubble = document.createElement("li");
	chatBubble.classList.add("userInput");

	//adds input of textarea to chatbubble list item
	chatBubble.innerHTML = input;

	//adds chatBubble to chatlist
	chatList.appendChild(chatBubble);

	//Sets chatlist scroll to bottom
	setTimeout(function () {
		chatList.scrollTop = chatList.scrollHeight;
	}, 0);

	botResponse(input);
};

// debugger;

function botResponse(textVal) {
    const formData = new FormData();
    formData.append("text", textVal);

    fetch("/gpt2-chat",
        {
            method: "POST",
            body: formData,
        }
    ).then(async response => {
        if (response.status == 200){
			reply = await response.text();
			if (reply === "timeout"){
				userBubble.innerHTML = responseText("죄송합니다. 다시 말씀해주세요.");
			}
			else{
				userBubble.innerHTML = responseText(reply);
			}
        }
        else if(response.status == 429){
			userBubble.innerHTML = responseText("죄송합니다. 다시 말씀해주세요.");
		}
        else{
            throw Error((await response.clone().json()).message);
        }
    }).catch(e => {
    	console.log(e)
		userBubble.innerHTML = responseText("죄송합니다. 다시 말씀해주세요.");
	})

	// reset text area input
	textInput.value = "";

}

function responseText(e) {
	var response = document.createElement("li");

	response.classList.add("bot__output");

	//Adds whatever is given to responseText() to response bubble
	response.innerHTML = e;

	chatList.appendChild(response);

	//Sets chatlist scroll to bottom
	setTimeout(function () {
		chatList.scrollTop = chatList.scrollHeight;
	}, 0);
}