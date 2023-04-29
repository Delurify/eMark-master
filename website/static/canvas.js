// For canvas page
var stageHeight = 500;
var stageWidth = 800;
var rectArray = [];
var circleArray = [];
var textArray = [];
var anchorArray = [];
var imageArray = [];
var currentAnchor = -1;

const stage = new Konva.Stage({
  height: stageHeight,
  width: stageWidth,
  container: "konva-holder",
});

const layer = new Konva.Layer();
stage.add(layer);

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
    if (anchorArray.length > 0) {
      for (let i = 0; i < anchorArray.length; i++) {
        anchorArray[i].remove();
      }
    }
  });

  layer.add(imageKon);

  imageArray.push(imageKon);
};

var rectButton = document.getElementById("rectangletool");
rectButton.addEventListener("click", function () {
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

  var rectAnchor = new Konva.Transformer({
    nodes: [rect],
    keepRatio: true,
  });

  rect.on("click tap", function () {
    layer.add(rectAnchor);
  });

  layer.add(rect);
  layer.add(rectAnchor);

  anchorArray.push(rectAnchor);
  currentAnchor = anchorArray.length - 1;
});

var circleButton = document.getElementById("circletool");
circleButton.addEventListener("click", function () {
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

  var circleAnchor = new Konva.Transformer({
    nodes: [circle],
    keepRatio: true,
  });

  circle.on("click tap", function () {
    layer.add(circleAnchor);
  });

  layer.add(circle);
  layer.add(circleAnchor);

  anchorArray.push(circleAnchor);
  currentAnchor = anchorArray.length - 1;
});

var textButton = document.getElementById("texttool");
textButton.addEventListener("click", function () {
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

  var textAnchor = new Konva.Transformer({
    nodes: [simpleText],
    keepRatio: true,
    enabledAnchors: ["top-left", "top-right", "bottom-left", "bottom-right"],
  });

  simpleText.on("click tap", function () {
    layer.add(textAnchor);
  });

  simpleText.on("dblclick dbltap", () => {
    //create text over canvas with absolute position
    var textPosition = textNode.getAbsolutePosition();

    var stageBox = stage.container().getBoundingClientRect();

    // so position of textarea will be the sum of positions above:
    var areaPosition = {
      x: stageBox.left + textPosition.x,
      y: stageBox.top + textPosition.y,
    };

    // create textarea and style it
    var textarea = document.createElement("textarea");
    document.body.appendChild(textarea);

    textarea.value = textNode.text();
    textarea.style.position = "absolute";
    textarea.style.top = areaPosition.y + "px";
    textarea.style.left = areaPosition.x + "px";
    textarea.style.width = textNode.width();

    textarea.focus();
    textarea.addEventListener("keydown", function (e) {
      // hide on enter
      if (e.keyCode === 13) {
        simpleText.text(textarea.value);
        document.body.removeChild(textarea);
      }
    });
  });

  layer.add(simpleText);
  layer.add(textAnchor);

  textArray.push(simpleText);
  anchorArray.push(textAnchor);
  currentAnchor = anchorArray.length - 1;
});
