var stageHeight = 500;
var stageWidth = 800;

const stage = new Konva.Stage({
  height: stageHeight,
  width: stageWidth,
  container: "konva-holder",
});

const layer = new Konva.Layer();
stage.add(layer);
//create Rectangle
var rect = new Konva.Rect({
  x: 50,
  y: 50,
  height: 100,
  width: 200,
  fill: "white",
  stroke: "orange",
  strokeWidth: 2,
  cornerRadius: 8,
  draggable: true,
});

//create Circle
var circle = new Konva.Circle({
  x: 150,
  y: 150,
  radius: 70,
  fill: "white",
  stroke: "orange",
  strokeWidth: 2,
  draggable: true,
});

//create text
var simpleText = new Konva.Text({
  x: stage.width() / 2 - 40,
  y: stage.height() / 2 + 40,
  text: "Sample Text",
  fontSize: 30,
  fontFamily: "Calibri",
  fill: "black",
  draggable: true,
});

var imageObj = new Image();
imageObj.src = "/static/image/watermarked.jpg";

imageObj.onload = function () {
  const aspectRatio = imageObj.width / imageObj.height;
  var imageHeight = imageObj.height;
  var imageWidth = imageObj.width;

  if (imageObj.height > stageHeight || imageObj.width > stageWidth) {
    if (aspectRatio > 1) {
      // image is wider than tall
      imageWidth = stageWidth;
      imageHeight = imageWidth / aspectRatio;
    } else {
      // image is taller than wide
      imageHeight = stageHeight;
      imageWidth = imageHeight * aspectRatio;
    }
  }

  var imageKon = new Konva.Image({
    x: (stageWidth - imageWidth) / 2,
    y: (stageHeight - imageHeight) / 2,
    image: imageObj,
    width: imageWidth,
    height: imageHeight,
  });

  imageKon.on("click", function () {
    textAnchor.remove();
  });

  layer.add(imageKon);
};

var rectButton = document.getElementById("rectangletool");
rectButton.addEventListener("click", function () {
  layer.add(rect);
});

var circleButton = document.getElementById("circletool");
circleButton.addEventListener("click", function () {
  layer.add(circle);
});

var textAnchor = new Konva.Transformer({
  nodes: [simpleText],
  keepRatio: true,
  enabledAnchors: ["top-left", "top-right", "bottom-left", "bottom-right"],
});

var textButton = document.getElementById("texttool");
textButton.addEventListener("click", function () {
  layer.add(simpleText);
  layer.add(textAnchor);
});

//Manage Anchors
//Remove all anchors
function removeAnchor() {
  textAnchor.remove();
}
background.on("click", removeAnchor);

simpleText.on("click", function () {
  layer.add(textAnchor);
});
