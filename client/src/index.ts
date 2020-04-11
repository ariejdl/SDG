
import { Terminal } from 'xterm';
import * as d3 from 'd3';
import { X } from './component';
require('./animation');

import './base.scss';

let _mainHTML;
let _mainCanvas;
let _mainContext;
const devicePixelRatio = window.devicePixelRatio || 1;

function updateCanvasSize() {
    _mainCanvas.width = window.innerWidth * devicePixelRatio;
    _mainCanvas.height = window.innerHeight * devicePixelRatio;
    // update context
    _mainContext.scale(devicePixelRatio, devicePixelRatio);
}

function windowResize() {
    updateCanvasSize();
}

let i = 0;

class CanvasObject {

    private z;

    render() {
    }
    
}

class HTMLObject {

    private z;

    render() {
    }
    
}

class Scene {

    constructor() {
        this.canvasObjects = [];
        this.htmlObjects = [];
    }

    addCanvasObject(obj: CanvasObject) {
        this.canvasObjects.push(obj);
    }

    addHTMLObject(obj: HTMLObject) {
        this.htmlObjects.push(obj);
    }

    renderCanvas(ctx) {
        for (let i = 0; i < this.canvasObjects.length; i++) {
            this.canvasObjects[i].render();
        }
    }
    
}

function render() {

    const width = window.innerWidth,
          height = window.innerHeight;

    const ctx = _mainContext;

    ctx.clearRect(0, 0, width, height);
    
    ctx.fillStyle = "rgba(0,0,0,1.0)";
    ctx.strokeStyle = "rgba(0,0,0,1.0)";
    ctx.lineWidth = 10;

    ctx.beginPath();
    ctx.moveTo(100 + Math.sin(i / 10) * 20, 100);
    ctx.lineTo(200 + Math.sin(i / 10) * 20, 200);
    ctx.closePath();
    ctx.stroke();

    //i += 1;

    requestAnimationFrame(render);
}

function setupHTMLBase() {
    _mainHTML = document.createElement('section');
    _mainHTML.className = "full-size";
    document.body.appendChild(_mainHTML);
}

function setupCanvas() {
    
    _mainCanvas = document.createElement('canvas');
    _mainCanvas.className = "full-size";
    document.body.appendChild(_mainCanvas);
    _mainContext = _mainCanvas.getContext("2d");
    
    updateCanvasSize();

    requestAnimationFrame(render);
}

function HTMLArea() {
    // add a clip path to integrate nicely with Canvas
    // https://css-tricks.com/clipping-masking-css/
}

document.addEventListener('DOMContentLoaded', function() {
    console.log(d3.scalePow(), d3.scaleLog(), Terminal, X, 55);

    setupHTMLBase();
    setupCanvas();
    window.onresize = windowResize;
});
