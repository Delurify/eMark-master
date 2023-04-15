var stageHeight = 450;
var stageWidth = 800;

const stage = new Konva.Stage({
    height: stageHeight,
    width: stageWidth,
    container:"konva-holder",
});

const layer = new Konva.Layer();
stage.add(layer);

const stageBorder = new Konva.Rect({
    x: 0,
    y: 0,
    stroke: "black",
    strokeWidth: 1,
    height: stage.height(),
    width: stage.width(),
});
layer.add(stageBorder)


var imageObj = new Image();
imageObj.src = "/static/image/watermarked.jpg";

imageObj.onload = function () {

    const aspectRatio = imageObj.width / imageObj.height;
    var imageHeight = imageObj.height;
    var imageWidth = imageObj.width;

    if (imageObj.height > stageHeight || imageObj.width > stageWidth) {
        if (aspectRatio > 1) { // image is wider than tall
            imageWidth = stageWidth;
            imageHeight = imageWidth / aspectRatio;
        } else { // image is taller than wide
            imageHeight = stageHeight;
            imageWidth = imageHeight * aspectRatio;
        }
    }

    var imageKon = new Konva.Image({
        x: 5,
        y: 5,
        image: imageObj,
        width: imageWidth * 0.8,
        height: imageHeight * 0.8,
        draggable: true,
    });

    layer.add(imageKon);
};


var rectButton = document.getElementById('rectangletool');
rectButton.addEventListener('click', function(){
    //create new shape
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
    })

    layer.add(rect);
})

var circleButton = document.getElementById('circletool');
circleButton.addEventListener('click', function(){
    //create new shape
    var circle = new Konva.Circle({
        x: 150,
        y: 150,
        radius: 70,
        fill: "white",
        stroke: "orange",
        strokeWidth: 2,
        draggable: true,
    })

    layer.add(circle);
})
