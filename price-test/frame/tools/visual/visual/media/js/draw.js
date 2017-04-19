
HorizonImg = "_horizon.png";
VerticalImg = "_vertical.png";
SlashImg = "_slash.png";
BackslashImg = "_backslash.png";
	
//只画出来这个img
function drawImgAsBackground(src, x, y, shiftx, shifty, width, height){
    x = x + shiftx;
    y = y + shifty;
    var div = document.createElement('div');
    div.innerHTML =
          "<div style ='position:absolute;  left:" + x + "px;" + 
            "top:" + y + "px; " + 
            "width:" + width + "px; " + 
            "height:" + height + "px; " + 
            "background-image: url(" + src + ");' >"+
            "</div>";
    document.getElementById(drawId).appendChild(div);
}

//画一个模块
function drawModule(src, word, x, y, shiftx, shifty){
    x = x + shiftx;
    y = y + shifty;
    var div = document.createElement('div');
    div.innerHTML =
          "<div style ='background:#EEEEEE;position:absolute;  left:" + x + "px;" + 
            "top:" + y + "px; " + 
            "' >"+
            "<image src = '" + src + "' alt = '" + word +"' />" + 
            word +
            "</div>";
    document.getElementById(drawId).appendChild(div);
}


//画一个模块
function drawLogIframe(src, x, y, shiftx, shifty, width, height){
    savedDrawId = drawId;
    drawId = "log";
    x = x + shiftx;
    y = y + shifty;
    var div = document.createElement('div');
    
    div.innerHTML =
          "<div style ='position:absolute;  left:" + x + "px;" + 
            "top:" + y + "px; " + 
            "' >"+
            "<iframe src='" + src + "' width='" + width + "' height='" + height + "' />" + 
            "</div>";
    document.getElementById(drawId).appendChild(div);
    drawId = savedDrawId;
}


function drawDivImg(src, x, y, shiftx, shifty, width, height){
    x = x + shiftx;
    y = y + shifty;
    var div = document.createElement('div');
    div.innerHTML =
          "<div style ='position:absolute;  left:" + x + "px;" + 
            "top:" + y + "px; " + 
            "width:" + width + "px; " + 
            "height:" + height + "px;' >" + 
            "<img src=" + src + " alt='" + src + "' "+
            "width=" + width + "px; " + 
            "height=" + height + "px; " + 
            "/>"+
            "</div>";
    document.getElementById(drawId).appendChild(div);
}

function drawImg(src, x, y, shiftx, shifty, width, height){
    x = x + shiftx;
    y = y + shifty;
    var div = document.createElement('div');
    div.innerHTML =
          "<div style ='position:absolute;  left:" + x + "px;" + 
            "top:" + y + "px; " + 
            "width:" + width + "px; " + 
            "height:" + height + "px; " + 
            "background-image: url(" + src + ");' >"+
            "</div>";
    
    document.getElementById(drawId).appendChild(div);
}


//画横线 y1 < y2
function drawHorizontalLine(x1, x2, y){
    drawImg("img/"+color+HorizonImg, x1, y, SHIFTX, SHIFTY, x2-x1, LINEBORDER );
} 
//画竖线 x1 < x2
function drawVerticalLine(x, y1, y2){
    drawImg("img/"+color+VerticalImg, x, y1, SHIFTX, SHIFTY, LINEBORDER, y2-y1 );
}
//画/线 x1 < x2, y1 > y2
function drawSlashLine(x1, y1, x2, y2){
    drawDivImg("img/"+color+SlashImg, x1, y2, SHIFTX, SHIFTY, x2 - x1, y1 - y2);
}
//画\线 x1 < x2, y1 < y2
function drawBackslashLine(x1, y1, x2, y2){
    drawDivImg("img/"+color+BackslashImg, x1, y1, SHIFTX, SHIFTY, x2 - x1, y2 - y1);
}
	
function drawLine(x1, y1, x2, y2){
    if(x1 == x2){
        drawVerticalLine(x1, Math.min(y1, y2), Math.max(y1, y2));
        return;
    }
    if(y1 == y2){
        drawHorizontalLine(Math.min(x1, x2), Math.max(x1, x2), y1);
        return;
    }
    if(x1 > x2 && y1 > y2){
        drawBackslashLine(x2, y2, x1, y1);
        return;
    }
    if(x1 < x2 && y1 < y2){
        drawBackslashLine(x1, y1, x2, y2);
        return;
    }
    if(x1 > x2 && y1 < y2){
        drawSlashLine(x2, y2, x1, y1);
        return;
    }
    if(x1 < x2 && y1 > y2){
        drawSlashLine(x1, y1, x2, y2);
        return;
    }
    alert("Error in drawLine: arguments: "+ x1 + "," + x2 + "," + y1 + "," + y2)
}



function drawDibiaoImg(src, x, y, width, height, text){
    x = x + spaceX
    y = y + spaceY
    var div = document.createElement('div');
    div.innerHTML =
          "<div style ='position:absolute;  left:" + (x - width/2) + "px;" + 
            "top:" + (y - height/2) + "px; " + 
            "width:" + width + "px; " + 
            "height:" + height + "px; " +
            "background-image: url(" + src + ")"+
            "\'>" + 
            "</div>";
    document.getElementById(drawId).appendChild(div);
    var div = document.createElement('div');
    div.innerHTML =
          "<div style ='position:absolute;  left:" + (x - width/2) + "px;" + 
            "top:" + (y - height/2) + "px; " + 
            "height:" + height + "px; " +
            "\'>" + "　"+text+
            "</div>";
    document.getElementById(drawId).appendChild(div);
}
    
    
