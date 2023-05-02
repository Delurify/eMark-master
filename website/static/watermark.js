// For basic watermark embedding page.
const fileInput = document.getElementById("image_input"),
  chooseImgBtn = document.querySelector(".choose-img"),
  batchInput = document.getElementById("image_batch"),
  multipleImgBtn = document.querySelector(".multiple-img");
previewImg = document.querySelector(".preview-img img");
const embedBtn = document.querySelector(".embed");

//Try new code to load the image uploaded
const loadImage = () => {
  let file = fileInput.files[0]; //getting user selected file
  if (!file) return; //return if user hasn't selected file
  previewImg.src = URL.createObjectURL(file); //passing file url as preview img src
  embedBtn.removeAttribute("hidden");
};

const loadImageBatch = () => {
  let file = batchInput.files[0]; //getting user selected file
  if (!file) return; //return if user hasn't selected file
  previewImg.src = URL.createObjectURL(file); //passing file url as preview img src
  embedBtn.removeAttribute("hidden");
};

chooseImgBtn.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", loadImage);

multipleImgBtn.addEventListener("click", () => batchInput.click());
batchInput.addEventListener("change", loadImageBatch)
