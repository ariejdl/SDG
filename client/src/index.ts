
//import { Terminal } from 'xterm';

import { setupHTMLBase, setupCanvas, windowResize } from './scene';

import { DockPanel } from '@lumino/widgets';
import { ResizeMessage, Widget } from '@lumino/widgets';

import './base.scss';
import '@lumino/widgets/style/index.css';

import './panel.scss';

function createContent(title: string): Widget {
  var widget = new Widget();
  widget.addClass('content');
  widget.addClass(title.toLowerCase());

  widget.title.text = title;
  widget.title.closable = true;

  return widget;
}

document.addEventListener('DOMContentLoaded', function() {

    var panel = new DockPanel({ spacing: 0 });

    var w1 = createContent('Red');
    var w2 = createContent('Green');
    var w3 = createContent('Blue');

    panel.addWidget(w1);
    panel.addWidget(w2);
    panel.addWidget(w3, { mode: 'split-right', ref: w2 });

    panel.id = 'base';

    panel.activate();

    //document.body.appendChild(panel.node);
    panel.show();
    //panel.parent = document.body;

    Widget.attach(panel, document.body);

    window.onresize = () => { panel.update() };

    /*
    setupHTMLBase();
    setupCanvas();
    window.onresize = windowResize;
    */
});
