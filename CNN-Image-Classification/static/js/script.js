
function previewImage(event) {
  const image = document.getElementById('imagePreview');
  image.innerHTML = '';
  const file = event.target.files[0];
  const reader = new FileReader();

  reader.onload = function() {
    const img = document.createElement('img');
    img.src = reader.result;
    image.appendChild(img);
  };

  if (file) {
    reader.readAsDataURL(file);
  }
}

async function predictImage() {
  const fileInput = document.getElementById('imageUpload');
  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Prediction request failed. Status: ' + response.status);
    }

    const data = await response.json();

    const predictionResult = document.getElementById('predictionResult');
    if (data.prediction === 'happy') {
      predictionResult.innerHTML = '<div class="alert alert-success prediction-alert" role="alert">Happy 😃</div>';
    } else if (data.prediction === 'sad') {
      predictionResult.innerHTML = '<div class="alert alert-danger prediction-alert" role="alert">Sad 😢</div>';
    } else {
      predictionResult.innerHTML = '<div class="alert alert-warning prediction-alert" role="alert">Model could not predict the image. Try another one.</div>';
    }
  } catch (error) {
    console.error('Error:', error.message);
    alert('Prediction failed. Please try again.');
  }
}
