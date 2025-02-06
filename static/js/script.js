document.getElementById("word").addEventListener("input", function () {
    fetch("/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ word: this.value })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("translation").value = data.translation;
        checkFormCompletion();
    });
});

// Audio recording functionality
let mediaRecorder;
let audioChunks = [];
let audioBlob;
let audioElement = document.getElementById("audioPlayer");
let audioInput = document.getElementById("audio");

document.getElementById("record").onclick = async () => {
    let stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.start();
    document.getElementById("record").disabled = true;
    document.getElementById("stop").disabled = false;
};

document.getElementById("stop").onclick = () => {
    mediaRecorder.stop();
    mediaRecorder.onstop = () => {
        audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        let audioUrl = URL.createObjectURL(audioBlob);

        // Set audio source
        audioElement.src = audioUrl;
        audioElement.style.display = "block";

        // Attach the recorded file to the form
        let file = new File([audioBlob], "recorded_audio.webm", { type: "audio/webm" });
        let dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        audioInput.files = dataTransfer.files;

        document.getElementById("record").disabled = false;
        document.getElementById("stop").disabled = true;

        checkFormCompletion();
    };
};

// Check if all fields are filled
function checkFormCompletion() {
    const word = document.getElementById("word").value.trim();
    const transit = document.getElementById("transit").value.trim();
    const translation = document.getElementById("translation").value.trim();
    const audio = document.getElementById("audio").files.length;
    const image = document.getElementById("image").files.length;
    const submitButton = document.getElementById("submitBtn");

    // Show error messages if fields are empty
    document.getElementById("wordError").style.display = word ? "none" : "block";
    document.getElementById("transitError").style.display = transit ? "none" : "block";
    document.getElementById("audioError").style.display = audio ? "none" : "block";
    document.getElementById("imageError").style.display = image ? "none" : "block";

    // Enable submit button only if all fields are filled
    submitButton.disabled = !(word && transit && translation && audio && image);
}

// Listen for input changes
document.getElementById("word").addEventListener("input", checkFormCompletion);
document.getElementById("transit").addEventListener("input", checkFormCompletion);
document.getElementById("image").addEventListener("change", checkFormCompletion);

// Ensure form submission works correctly
document.getElementById("uploadForm").onsubmit = function (event) {
    event.preventDefault();
    
    let formData = new FormData(document.getElementById("uploadForm"));

    fetch("/", {
        method: "POST",
        body: formData
    })
    .then(response => response.text())
    .then(() => {
        document.getElementById("successMessage").textContent = "Upload successful!";
        document.getElementById("successMessage").style.display = "block";

        // Reset the form
        document.getElementById("uploadForm").reset();
        document.getElementById("audioPlayer").style.display = "none";
        document.getElementById("submitBtn").disabled = true;
    })
    .catch(error => {
        console.error("Error submitting form:", error);
        alert("Error submitting form.");
    });
};

document.getElementById("word").addEventListener("input", function () {
    let kannadaWord = this.value.trim();

    if (kannadaWord === "") {
        document.getElementById("transit").value = "";
        return;
    }

    // Fetch Transliteration
    fetch("/transliterate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ word: kannadaWord })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("transit").value = data.transit;
        checkFormCompletion();
    })
    .catch(error => console.error("Transliteration Error:", error));

    // Fetch Translation
    fetch("/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ word: kannadaWord })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("translation").value = data.translation;
    })
    .catch(error => console.error("Translation Error:", error));
});


