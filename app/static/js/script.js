let camera_button = document.querySelector("#start-camera");
let video = document.querySelector("#video");
let click_button = document.querySelector("#click-photo");
let canvas = document.querySelector("#canvas");
let dataurl = document.querySelector("#dataurl");
let dataurl_container = document.querySelector("#dataurl-container");

camera_button.addEventListener("click", async function () {
  let stream = null;

  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: false,
    });
  } catch (error) {
        alert(error.message);
    return;
  }

  video.srcObject = stream;
  console.log(video)

  video.style.display = "block";
  camera_button.style.display = "none";
  click_button.style.display = "block";
});

click_button.addEventListener("click", function () {
  canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
  let image_data_url = canvas.toDataURL("image/jpeg");

  dataurl.value = image_data_url;
  dataurl_container.style.display = "block";
});