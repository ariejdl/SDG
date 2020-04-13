
import * as d3 from 'd3';

import { Panel, Widget } from '@lumino/widgets';

require('./animation');

let _mainHTML;
let _mainCanvas;
let _mainContext;
let _mainScene: Scene;
let _mousePos: { x: number, y: number } = {};
let _zoom: any;
let _zoomState: any = d3.zoomIdentity;

const devicePixelRatio = window.devicePixelRatio || 1;

function updateCanvasSize() {
    _mainCanvas.width = window.innerWidth * devicePixelRatio;
    _mainCanvas.height = window.innerHeight * devicePixelRatio;
    // update context
    _mainContext.scale(devicePixelRatio, devicePixelRatio);
}

export function windowResize() {
    updateCanvasSize();
}

function mouseMove(e) {
    _mousePos = { x: e.clientX, y: e.clientY };
}

function mouseOut(e) {
    _mousePos = undefined;
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

    abstract render(ctx: any, zoomState: any, hoverOrDrag: boolean): void

    abstract containsPoint(x: number, y: number): boolean
    
}

class CanvasCircleObject extends SceneObject {

    private radius: number;

    constructor(config: any) {
        super(config)
        this.radius = config['radius'];
    }    

    render(ctx: any, zoomState: any, hoverOrDrag: boolean) {
        ctx.beginPath();
        ctx.arc(zoomState.applyX(this.x),
                zoomState.applyY(this.y),
                zoomState.k * this.radius,
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

    render(ctx: any, zoomState: any, hoverOrDrag: boolean) {
        ctx.beginPath();
        ctx.moveTo(zoomState.applyX(this.points[0][0]),
                   zoomState.applyY(this.points[0][1]));
        for (var i = 1; i < this.points.length; i++) {
            ctx.lineTo(zoomState.applyX(this.points[i][0]),
                       zoomState.applyY(this.points[i][1]));
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

    public container: HTMLElement;

    constructor(config) {
        super(config);
        this.container = document.createElement('div');
        this.container.appendChild(config['el']);
        this.container.style['position'] = 'absolute';
    }

    updateStyle() {
        this.container.style['transform'] = `translate(${this.x}px, ${this.y}px)`;
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

    renderCanvas(ctx: any, zoomState: any, mousePos: any) {

        let mouseCoord;
        if (mousePos !== undefined) {
            mouseCoord = zoomState.invert([mousePos.x, mousePos.y])
        }
        

        let len = this.canvasObjects.length;
        let topHover: number;

        if (mouseCoord !== undefined) {
            while (len--) {
                if (this.canvasObjects[len].containsPoint(mouseCoord[0], mouseCoord[1])) {
                    topHover = len;
                    break;
                }
            }
        }

        for (let i = 0; i < this.canvasObjects.length; i++) {
            this.canvasObjects[i].render(ctx, zoomState, topHover === i);
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

    _mainScene.renderCanvas(ctx, _zoomState, _mousePos);

    requestAnimationFrame(render);
}

export function setupHTMLBase(parent) {
    _mainHTML = document.createElement('section');
    _mainHTML.className = "full-size";
    parent.appendChild(_mainHTML);
}

function setupZoom() {
    _zoom = d3.zoom()
    	  .scaleExtent([1/10, 4])
          .on("zoom", null) // reset callback
    	  .on("zoom", () => {
              _zoomState = d3.event.transform;

              d3.select(_mainHTML)
                  .style("transform",
                         `translate(${_zoomState.x}px,${_zoomState.y}px) scale(${_zoomState.k})`)
                  .style("transform-origin", "0 0");

          });

    d3.select(_mainCanvas)
        .call(_zoom)
        .on("wheel", null)
        .on("wheel", function(e) {
            d3.event.preventDefault();
            return false;
        });    
}

function sampleData() {
        // sample data
    d3.range(100).map((i) => {
        const x = 40;
        const y = 50;

        // hexagon
        const obj = new CanvasPolygonObject({
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
        });
        
        _mainScene.addCanvasObject(obj);
    });

    d3.range(300).map((i) => {
        const obj = new CanvasCircleObject({
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
            radius: 10
        });
        
        _mainScene.addCanvasObject(obj);
    });

    d3.range(5).map((i) => {
        const obj = new HTMLObject({
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
            el: simpleTable()
        });

        _mainHTML.appendChild(obj.container);
        obj.updateStyle();
    });
}

export function setupCanvas(parent) {
    
    _mainCanvas = document.createElement('canvas');
    _mainCanvas.className = "full-size";
    parent.appendChild(_mainCanvas);
    _mainContext = _mainCanvas.getContext("2d");

    updateCanvasSize();

    _mainCanvas.addEventListener('mousemove', mouseMove);
    _mainCanvas.addEventListener('mouseout', mouseOut);    
    
    _mainScene = new Scene();

    setupZoom();

    sampleData();

    requestAnimationFrame(render);
}

const simpleTable = () => {
    const t = document.createElement('table');
    const tbody = document.createElement('tbody');
    d3.range(10).map((i) => {
        const tr = document.createElement('tr');
        d3.range(5).map((j) => {
            const td = document.createElement('td');
            td.innerText = i + j;
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    t.appendChild(tbody);
    return t;
}

function HTMLArea() {
    // add a clip path to integrate nicely with Canvas
    // https://css-tricks.com/clipping-masking-css/
}

// watercolor/sketch webgl effect, can use this, reduce number of samples
// https://www.shadertoy.com/view/ltyGRV

export class SceneWidget extends Panel {

    constructor() {
        super();
        this._widget = new Widget();
        this.addWidget(this._widget);

        setupHTMLBase(this._widget.node);
        setupCanvas(this._widget.node);
    }
}
