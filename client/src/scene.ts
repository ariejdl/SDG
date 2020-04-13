
import * as d3 from 'd3';

import { Panel, Widget } from '@lumino/widgets';

require('./animation');

const devicePixelRatio = window.devicePixelRatio || 1;

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

    constructor(config: any) {
        super(config)
        this.points = config['points'];
    }

    render(ctx: any, zoomState: any, hoverOrDrag: boolean) {
        ctx.beginPath();
        ctx.moveTo(zoomState.applyX(this.x + this.points[0][0]),
                   zoomState.applyY(this.y + this.points[0][1]));
        for (var i = 1; i < this.points.length; i++) {
            ctx.lineTo(zoomState.applyX(this.x + this.points[i][0]),
                       zoomState.applyY(this.y + this.points[i][1]));
        }
        ctx.closePath();
        if (hoverOrDrag) {
            ctx.fill();
        }
        ctx.stroke();  
    }

    containsPoint(x: number, y: number): boolean {
        return d3.polygonContains(this.points, [x - this.x, y - this.y]);
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

    public draggingObject: CanvasObject;

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

        if (topHover !== undefined) {
            this.draggingObject = this.canvasObjects[len];
        } else {
            this.draggingObject = undefined;
        }

        for (let i = 0; i < this.canvasObjects.length; i++) {
            this.canvasObjects[i].render(ctx, zoomState, topHover === i);
        }
    }
    
}

function sampleData(scene, html) {
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
        
        scene.addCanvasObject(obj);
    });

    d3.range(300).map((i) => {
        const obj = new CanvasCircleObject({
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
            radius: 10
        });
        
        scene.addCanvasObject(obj);
    });

    d3.range(5).map((i) => {
        const obj = new HTMLObject({
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
            el: simpleTable()
        });

        html.appendChild(obj.container);
        obj.updateStyle();
    });
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

// inertia
// https://bl.ocks.org/pjanik/raw/5872514/
// probably can extract this from d3.v2

export class SceneWidget extends Panel {

    private tick: number = 0;
    private _mainHTML;
    private  _mainCanvas;
    private _mainContext;
    private _mainScene: Scene;
    private _mousePosOffset: { x: number, y: number } = { x: 0, y: 0 };
    private _mousePos: { x: number, y: number } = {};
    private _zoom: any;
    private _zoomState: any = d3.zoomIdentity;

    private _isZooming: boolean = false;
    private _isDraggingSceneObject: boolean = false;
    
    constructor() {
        super();
        this._widget = new Widget();
        this.addWidget(this._widget);

        this.setupHTMLBase(this._widget.node);
        this.setupCanvas(this._widget.node);        

        // TODO: remove
        sampleData(this._mainScene, this._mainHTML);
    }

    protected onResize(msg: Widget.ResizeMessage): void {
        this._mainCanvas.width = msg.width * devicePixelRatio;
        this._mainCanvas.height = msg.height * devicePixelRatio;
        // update context
        this._mainContext.scale(devicePixelRatio, devicePixelRatio);

        const rect = this._mainCanvas.getBoundingClientRect();
        this._mousePosOffset = { x: rect.left, y: rect.top };
    }

    mouseMove(e) {
        if (this._isZooming) {
            return;
        }
        this._mousePos = { x: e.clientX, y: e.clientY };
    }

    mouseOut(e) {
        this._mousePos = undefined;
    }

    setupCanvas(parent) {
        
        this._mainCanvas = document.createElement('canvas');
        this._mainCanvas.className = "full-size";
        this._mainCanvas.style['background'] = "white";
        parent.appendChild(this._mainCanvas);
        this._mainContext = this._mainCanvas.getContext("2d");

        this._mainCanvas.addEventListener('mousemove', this.mouseMove.bind(this));
        this._mainCanvas.addEventListener('mouseout', this.mouseOut.bind(this));    
        
        this._mainScene = new Scene();

        this.setupZoom();

        requestAnimationFrame(this.render.bind(this));
    }

    setupHTMLBase(parent) {
        // TODO: fix scroll behaviour, getting caught on HTML elements
        this._mainHTML = document.createElement('section');
        this._mainHTML.className = "full-size";
        parent.appendChild(this._mainHTML);
    }

    setupZoom() {
        this._zoom = d3.zoom()
    	    .scaleExtent([1/10, 4])
            .on("zoom", null) // reset callback
            .on("start", () => {
                this._isZooming = true;
            })
            .on("end", () => {
                this._isZooming = false;
                this._isDraggingSceneObject = false;
                this._mainScene.draggingObject = undefined;
            })
    	    .on("zoom", () => {

                let dragOnly = (this._zoomState.k - d3.event.transform.k) === 0;

                if (this._mainScene.draggingObject !== undefined &&
                    (dragOnly || this._isDraggingSceneObject)) {
                    
                    this._isDraggingSceneObject = true;

                    const coordinate = d3.event.transform.apply([
                        d3.event.sourceEvent.clientX,
                        d3.event.sourceEvent.clientY
                    ]);

                    console.log(coordinate);

                    this._mainScene.draggingObject.update(
                        coordinate[0], coordinate[1]);
                    
                    return;
                }
                
                this._zoomState = d3.event.transform;

                d3.select(this._mainHTML)
                    .style("transform",
                           `translate(${this._zoomState.x}px,${this._zoomState.y}px) scale(${this._zoomState.k})`)
                    .style("transform-origin", "0 0");

            });

        d3.select(this._mainCanvas)
            .call(this._zoom)
            .on("wheel", null)
            .on("wheel", function(e) {
                d3.event.preventDefault();
                return false;
            });    
    }

    protected onAfterAttach() {
        this.node.addEventListener('scroll', this, true);
    }

    protected onBeforeDetach() {
        this.node.removeEventListener('scroll', this, true);
    }

    handleEvent(event: Event): void {
        switch (event.type) {
        case 'scroll':
            this._clearHover();
            break;
        default:
            break;
        }
    }    

    render() {

        const width = window.innerWidth,
              height = window.innerHeight;

        const ctx = this._mainContext;

        ctx.clearRect(0, 0, width, height);
        
        ctx.fillStyle = "rgba(0,0,0,1.0)";
        ctx.strokeStyle = "rgba(0,0,0,1.0)";

        this.tick += 1;

        ctx.lineWidth = 2;

        this._mainScene.renderCanvas(ctx, this._zoomState,
                                     this._mousePos !== undefined ?
                                     { x: this._mousePos.x - this._mousePosOffset.x,
                                       y: this._mousePos.y - this._mousePosOffset.y } : undefined);

        requestAnimationFrame(this.render.bind(this));
    }
    
}