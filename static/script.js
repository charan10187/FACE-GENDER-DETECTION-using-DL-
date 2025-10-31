let uploadedFile = null;

// ✅ Updates filename when an image is selected
function updateFileName() {
    let input = document.getElementById("imageUpload");
    if (input.files.length > 0) {
        uploadedFile = input.files[0];
        document.getElementById("file-name").innerText = uploadedFile.name;
        document.getElementById("predictBtn").disabled = false;  // Enable Predict button
    } else {
        document.getElementById("file-name").innerText = "No file chosen";
        document.getElementById("predictBtn").disabled = true;  // Disable Predict button
    }
}

// ✅ Upload function (doesn't send to server, just stores the file)
function uploadImage() {
    let fileInput = document.getElementById("imageUpload");

    if (!fileInput.files.length) {
        alert("❌ Please select an image first!");
        return;
    }

    uploadedFile = fileInput.files[0];
    document.getElementById("file-name").innerText = uploadedFile.name;
    document.getElementById("predictBtn").disabled = false;  // Enable Predict button
}

// ✅ Predict function (sends uploaded file to the server)
function predictImage() {
    if (!uploadedFile) {
        alert("❌ Please upload an image first!");
        return;
    }

    let formData = new FormData();
    formData.append("image", uploadedFile);

    fetch("/predict", { method: "POST", body: formData })
    .then(response => response.json())
    .then(data => {
        document.getElementById("result").innerText = `Predicted Age: ${data.age}, Gender: ${data.gender}`;
        addToHistory(URL.createObjectURL(uploadedFile), data.age, data.gender);
    })
    .catch(error => {
        console.error("Error:", error);
        alert("❌ Prediction failed. Check console.");
    });
}

// ✅ Webcam setup
let video = document.getElementById("video");
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => { video.srcObject = stream; })
    .catch(error => console.error("❌ Webcam Error:", error));

// ✅ Capture image and send for prediction
function captureImage() {
    let canvas = document.createElement("canvas");
    let context = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    let imageDataUrl = canvas.toDataURL("image/jpeg");

    canvas.toBlob(blob => {
        let formData = new FormData();
        formData.append("image", blob, "captured_image.jpg");

        fetch("/capture", { method: "POST", body: formData })
        .then(response => response.json())
        .then(data => {
            document.getElementById("result").innerText = `Predicted Age: ${data.age}, Gender: ${data.gender}`;
            addToHistory(imageDataUrl, data.age, data.gender);
        })
        .catch(error => {
            console.error("Error:", error);
            alert("❌ Capture Prediction failed.");
        });
    }, "image/jpeg");
}

// ✅ Add prediction to history
function addToHistory(imageUrl, age, gender) {
    let history = document.getElementById("history");
    let historyEntry = `
        <div class="history-item">
            <img src="${imageUrl}" class="history-img">
            <span class="history-text">Age: ${age}, Gender: ${gender}</span>
        </div>`;
    history.innerHTML = historyEntry + history.innerHTML;
}

// ✅ Show popup notification
function showPopup(age, gender) {
    let popup = document.getElementById("popup");
    popup.innerText = `✅ Age: ${age}, Gender: ${gender}`;
    popup.style.display = "block";
    popup.style.opacity = "1";
    setTimeout(() => {
        popup.style.opacity = "0";
        setTimeout(() => { popup.style.display = "none"; }, 500);
    }, 2000);
}
