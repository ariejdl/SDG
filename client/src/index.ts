
//import { Terminal } from 'xterm';

import { SceneWidget } from './scene';

import { DockPanel } from '@lumino/widgets';
import { ResizeMessage, Widget } from '@lumino/widgets';

import './base.scss';
import '@lumino/widgets/style/index.css';

import './panel.scss';

function createContent(title: string): Widget {
  var widget = new Widget();
  widget.addClass('content');
  widget.addClass(title.toLowerCase());

  widget.title.label = title;
  widget.title.closable = true;

  return widget;
}

document.addEventListener('DOMContentLoaded', function() {

    // https://github.com/jupyterlab/lumino/tree/master/packages/widgets
    var panel = new DockPanel({ spacing: 0 });

    let scene = new SceneWidget();

    var w1 = createContent('Red');
    var w2 = createContent('Green');
    var w3 = createContent('Blue');

    panel.addWidget(scene);
    panel.addWidget(w2);
    //panel.addWidget(w3, { mode: 'split-right', ref: w2 });

    panel.id = 'base';

    panel.activate();

    //document.body.appendChild(panel.node);
    panel.show();
    //panel.parent = document.body;

    Widget.attach(panel, document.body);

    window.onresize = () => { panel.update() };

    /*
    setupHTMLBase(visualsWidget);
    setupCanvas(visualsWidget);
    window.onresize = windowResize;
    */
});
