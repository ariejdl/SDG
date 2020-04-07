
import { Terminal } from 'xterm';
import * as d3 from 'd3';

import './base.scss';

export class C {
    private x = 10;
    getX = () => this.x;
    setX = (newVal: number) => { this.x = newVal; }
}

export let x = new C();
export let y = { ...{ some: "value" } };

document.addEventListener('DOMContentLoaded', function() {
    console.log(d3, Terminal)
});
