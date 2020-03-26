
var ws = new WebSocket("ws://localhost:8888/echo");
ws.onopen = function() {
    ws.send("Hello, world " + new Date().getSeconds())
};
ws.onmessage = function (evt) {
   console.log(evt.data);
};

/* treat this as a kind of unit test for back-end to begin with */

function wsKernel(kernelID) {
    var ws = new WebSocket("ws://localhost:8888/api/kernels/" + kernelID + "/channels");
    ws.onopen = function() {

        ws.send(JSON.stringify({"header":{"msg_id":"eede5f7d23a241549c9d8969cde0ca9d","username":"username","session":"eb1877a990f840a799612468b2f8edfd","msg_type":"kernel_info_request","version":"5.2"},"metadata":{},"content":{},"buffers":[],"parent_header":{},"channel":"shell"}))

        ws.send(JSON.stringify({"header":{"msg_id":"648d5b4b96204a4f8e4243f22a1f7e1a","username":"username","session":"eb1877a990f840a799612468b2f8edfd","msg_type":"comm_info_request","version":"5.2"},"metadata":{},"content":{"target_name":"jupyter.widget"},"buffers":[],"parent_header":{},"channel":"shell"}));

        ws.send(JSON.stringify({"header":{"msg_id":"3d6ff0592ffd47048373e804b2dad752","username":"username","session":"eb1877a990f840a799612468b2f8edfd","msg_type":"execute_request","version":"5.2"},"metadata":{},"content":{"code":"a = 1","silent":false,"store_history":true,"user_expressions":{},"allow_stdin":true,"stop_on_error":true},"buffers":[],"parent_header":{},"channel":"shell"}));

        ws.send(JSON.stringify({"header":{"msg_id":"a98c2f5bdc284d668f2b9b9e1cfc0cc5","username":"username","session":"eb1877a990f840a799612468b2f8edfd","msg_type":"execute_request","version":"5.2"},"metadata":{},"content":{"code":"print(a)","silent":false,"store_history":true,"user_expressions":{},"allow_stdin":true,"stop_on_error":true},"buffers":[],"parent_header":{},"channel":"shell"}));
        
        //ws.send("test");
    };
    ws.onmessage = function (evt) {
        console.log(evt.data);
    };
}

fetch('/api/kernels')
    .then(r => r.json())
    .then((r) => {

        console.log(r);
        
        if (!r['available'].length)
            throw "expected at least one item";

        r['running'].map((k) => {
            fetch('/api/kernels/' + k.kernel_id, {
                method: 'DELETE'
            });
        });

        fetch('/api/kernels', {
            method: 'POST',
            body: JSON.stringify({ 'name': r['available'][r['available'].length - 1] })
            //body: JSON.stringify({ 'name': r['available'][0] })
        }).then(r => r.json())
            .then((r) => {
                console.log(r);

                wsKernel(r.id);

                fetch('/api/kernels/' + r.id)
                    .then(r => r.json())
                    .then((r) => {
                        console.log('info:', r)
                    });

                return;
                fetch('/api/kernels/' + r.id + '/restart', { method: 'POST' })
                    .then(r => r.json())
                    .then((r) => {
                        console.log('restart:', r)
                    });

                fetch('/api/kernels/' + r.id + '/interrupt', { method: 'POST' })
                
            });
    });

