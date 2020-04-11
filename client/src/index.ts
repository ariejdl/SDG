
import { Terminal } from 'xterm';

import './base.scss';


import { setupHTMLBase, setupCanvas, windowResize } from './scene';

document.addEventListener('DOMContentLoaded', function() {
    setupHTMLBase();
    setupCanvas();
    window.onresize = windowResize;
});
