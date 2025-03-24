var myGameArea = {
    canvas : document.createElement("canvas"),
    start : function() {
        this.canvas.width = 1500;
        this.canvas.height = 850;
        this.context = this.canvas.getContext("2d");
        document.body.insertBefore(this.canvas, document.body.childNodes[0]);
        this.frameNo = 0;
        this.interval = setInterval(updateGameArea, 20);
        this.canvas.hidden = true;
        window.addEventListener('keydown', (event) => {
            myGameArea.keys = (myGameArea.keys || []);
            myGameArea.keys[event.code] = true;
        }, false);
        window.addEventListener('keyup', (event) => {
            myGameArea.keys[event.code] = false;
        }, false);
    },
    hide : function() {
        this.canvas.hidden = true;
    },
    show : function() {
        this.canvas.hidden = false;
    },
    clear : function() {
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
    },
    stop : function() {
        clearInterval(this.interval);
    }
}