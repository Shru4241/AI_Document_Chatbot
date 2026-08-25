const input = document.getElementById("questionInput");
const sendButton = document.getElementById("sendButton");
const chatMessages = document.getElementById("chatMessages");
const typing = document.getElementById("typing");
const clearButton = document.getElementById("clearChat");


function addMessage(role, text, sources = []) {

    const message = document.createElement("div");
    message.className = `message ${role}`;


    const avatar = document.createElement("div");
    avatar.className = "avatar";

    avatar.textContent =
        role === "user" ? "👤" : "🤖";


    const content = document.createElement("div");
    content.className = "message-content";


    const name = document.createElement("div");
    name.className = "message-name";

    name.textContent =
        role === "user"
            ? "You"
            : "AI Assistant";


    const textElement = document.createElement("div");
    textElement.className = "message-text";


    // Render AI response as Markdown
    if (typeof marked !== "undefined") {

        textElement.innerHTML =
            marked.parse(
                text || "No answer received."
            );

    } else {

        // Fallback if Markdown library is unavailable
        textElement.innerText =
            text || "No answer received.";

    }


    content.appendChild(name);
    content.appendChild(textElement);


    // Display sources
    if (sources && sources.length > 0) {

        const sourceBox =
            document.createElement("div");

        sourceBox.className = "sources";


        const sourceTitle =
            document.createElement("div");

        sourceTitle.className =
            "sources-title";

        sourceTitle.textContent =
            "📚 Sources";


        sourceBox.appendChild(sourceTitle);


        sources.forEach(source => {

            const sourceItem =
                document.createElement("div");

            sourceItem.className =
                "source-item";


            sourceItem.textContent =
                `📄 Page: ${source.page} | File: ${source.source}`;


            sourceBox.appendChild(sourceItem);

        });


        content.appendChild(sourceBox);

    }


    message.appendChild(avatar);
    message.appendChild(content);

    chatMessages.appendChild(message);


    // Scroll to latest message
    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}



async function sendMessage() {

    const question =
        input.value.trim();


    if (!question) {
        return;
    }


    // Add user's question
    addMessage(
        "user",
        question
    );


    // Clear input
    input.value = "";


    // Disable send button
    sendButton.disabled = true;


    // Show typing indicator
    typing.classList.remove("hidden");


    try {

        const response =
            await fetch("/chat", {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    question: question
                })

            });


        // Check HTTP response
        if (!response.ok) {

            const errorText =
                await response.text();


            console.error(
                "FastAPI Error:",
                response.status,
                errorText
            );


            throw new Error(
                `Server error: ${response.status}`
            );

        }


        const data =
            await response.json();


        // Debug information
        console.log(
            "Question:",
            question
        );

        console.log(
            "API Response:",
            data
        );


        // Hide typing indicator
        typing.classList.add("hidden");


        // Display AI answer
        addMessage(
            "assistant",
            data.answer ||
                "No answer received.",
            data.sources ||
                []
        );


    } catch (error) {

        typing.classList.add("hidden");


        console.error(
            "Chat Error:",
            error
        );


        addMessage(
            "assistant",
            "Sorry, something went wrong. Please check the FastAPI server."
        );

    } finally {

        // Always enable send button
        sendButton.disabled = false;

        input.focus();

    }

}



sendButton.addEventListener(
    "click",
    sendMessage
);



input.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage();

        }

    }
);



clearButton.addEventListener(
    "click",
    function() {

        chatMessages.innerHTML = "";


        addMessage(
            "assistant",
            "Chat cleared! 👋 Ask me a question about the Tata Motors Annual Report 2024-25."
        );

    }
);

