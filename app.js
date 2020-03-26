
var ws = new WebSocket("ws://localhost:8888/echo");
ws.onopen = function() {
    ws.send("Hello, world " + new Date().getSeconds())
};
ws.onmessage = function (evt) {
   console.log(evt.data);
};

/* treat this as a kind of unit test for back-end to begin with */

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
            body: JSON.stringify({ 'name': r['available'][0] })
        }).then(r => r.json())
            .then((r) => {
                console.log(r);

                fetch('/api/kernels/' + r.kernel_id)
                    .then(r => r.json())
                    .then((r) => {
                        console.log('info:', r)
                    });

                fetch('/api/kernels/' + r.kernel_id + '/restart', { method: 'POST' })
                    .then(r => r.json())
                    .then((r) => {
                        console.log('restart:', r)
                    });

                fetch('/api/kernels/' + r.kernel_id + '/interrupt', { method: 'POST' })
                
            });
    });

