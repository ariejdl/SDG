
import { Terminal } from 'xterm';
import * as d3 from 'd3';
import { X } from './component';
require('./animation');

import './base.scss';

let _mainHTML;
let _mainCanvas;
let _mainContext;
let _mainScene: Scene;
let _mousePos: { x: number, y: number } = {};

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

function mouseMove(e) {
    _mousePos = { x: e.clientX, y: e.clientY };
}

let tick = 0;

class SceneObject {
    
    private x: number;
    private y: number;
    private objectScale: number;

    constructor(config: any) {
        this.x = config['x'];
        this.y = config['y'];
    }
    
    serialize() {
        return {
            x: this.x,
            y: this.y
        };
    }

    update(x: number, y: number) {
        this.x = x;
        this.y = y;
    }

    updateScale(objectScale: number) {
        this.objectScale = objectScale;
    }
    
}

class CanvasObject extends SceneObject {

    abstract render(ctx: any, hoverOrDrag: boolean): void

    abstract containsPoint(x: number, y: number): boolean
    
}

class CanvasCircleObject extends SceneObject {

    private radius: number;

    constructor(config: any) {
        super(config)
        this.radius = config['radius'];
    }    

    render(ctx: any, hoverOrDrag: boolean) {
        ctx.beginPath();
        ctx.arc(this.x,
                this.y,
                this.radius,
                0,
                Math.PI * 2);
        if (hoverOrDrag) {
            ctx.fill();
        }
        ctx.stroke();
    }

    containsPoint(x: number, y: number): boolean {
        return Math.sqrt(
            Math.pow(x - this.x, 2) +
            Math.pow(y - this.y, 2)
        ) <= this.radius;
    }
    
}

class CanvasPolygonObject extends SceneObject {

    private points: number[];
    private polygon: any;

    constructor(config: any) {
        super(config)
        this.points = config['points'].map(([a,b]) => [this.x + a, this.y + b]);
        this.polygon = d3.polygonHull(this.points);
    }

    render(ctx: any, hoverOrDrag: boolean) {
        ctx.beginPath();
        ctx.moveTo(this.points[0][0], this.points[0][1]);
        for (var i = 1; i < this.points.length; i++) {
            ctx.lineTo(this.points[i][0], this.points[i][1]);
        }
        ctx.closePath();
        if (hoverOrDrag) {
            ctx.fill();
        }
        ctx.stroke();  
    }

    containsPoint(x: number, y: number): boolean {
        return d3.polygonContains(this.points, [x, y]);
    }    
    
}

class HTMLObject extends SceneObject {

    private container: HTMLElement;
    private el: HTMLElement;

    constructor(el) {
        this.container = document.createElement('div');
        this.container.appendChild(el);
        this.el = el;
    }

    updateStyle() {
        this.container.style['transform'] = `translate(${this.x}, ${this.y})`;
        this.el.style['transform'] = `scale(${this.objectScale})`;
    }

    serialize() {
        return {
            ...super.serialize()
        };
    }
    
}

class Scene {

    private _canvasObjectDragging: CanvasObject;

    constructor() {
        this.canvasObjects = [];
        this.htmlObjects = [];
    }

    addCanvasObject(obj: CanvasObject) {
        // this determines z order
        this.canvasObjects.push(obj);
    }

    removeCanvasObject(idx: number) {
        this.canvasObjects.splice(idx, 1);
    }

    addHTMLObject(obj: HTMLObject) {
        this.htmlObjects.push(obj);
    }

    removeHTMLObject(idx: number) {
        // this determines z order
        this.htmlObjects.splice(idx, 1);
    }

    renderCanvas(ctx: any, x: number, y: number) {

        let len = this.canvasObjects.length;
        let topHover: number;
        while (len--) {
            if (this.canvasObjects[len].containsPoint(x, y)) {
                topHover = len;
                break;
            }
        }

        for (let i = 0; i < this.canvasObjects.length; i++) {
            this.canvasObjects[i].render(ctx, topHover === i);
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

    tick += 1;

    ctx.lineWidth = 2;

    _mainScene.renderCanvas(ctx, _mousePos.x, _mousePos.y);

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

    _mainCanvas.addEventListener('mousemove', mouseMove);
    
    updateCanvasSize();

    _mainScene = new Scene();

    d3.range(100).map((i) => {
        const x = 40;
        const y = 50;
        _mainScene.addCanvasObject(
            new CanvasPolygonObject({
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
                points: [
                    [0.5 * x, 0    * y],
                    [1   * x, 0.33 * y],
                    [1   * x, 0.66 * y],
                    [0.5 * x, 1    * y],
                    [0   * x, 0.66 * y],
                    [0   * x, 0.33 * y]
                ]
            })
        )
    });

    d3.range(300).map((i) => {
        _mainScene.addCanvasObject(
            new CanvasCircleObject({
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
                radius: 10
            })
        )
    });    

    requestAnimationFrame(render);
}

function HTMLArea() {
    // add a clip path to integrate nicely with Canvas
    // https://css-tricks.com/clipping-masking-css/
}

document.addEventListener('DOMContentLoaded', function() {

    setupHTMLBase();
    setupCanvas();
    window.onresize = windowResize;
});
