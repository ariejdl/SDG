
var ws = new WebSocket("ws://localhost:8888/echo");
ws.onopen = function() {
    ws.send("Hello, world " + new Date().getSeconds())
};
ws.onmessage = function (evt) {
   console.log(evt.data);
};

/* treat this as a kind of unit test for back-end to begin with */

var uuid = function () {
    /**
     * http://www.ietf.org/rfc/rfc4122.txt
     */
    var s = [];
    var hexDigits = "0123456789abcdef";
    for (var i = 0; i < 32; i++) {
        s[i] = hexDigits.substr(Math.floor(Math.random() * 0x10), 1);
    }
    s[12] = "4";  // bits 12-15 of the time_hi_and_version field to 0010
    s[16] = hexDigits.substr((s[16] & 0x3) | 0x8, 1);  // bits 6-7 of the clock_seq_hi_and_reserved to 01

    var uuid = s.join("");
    return uuid;
};

function wsKernel(kernelID) {
    var ws = new WebSocket("ws://localhost:8888/api/kernels/" + kernelID + "/channels");
    ws.onopen = function() {

        // "username" and "session" keys seem to be optional but must be null for julia

        ws.send(JSON.stringify({"header":{"msg_id":uuid(),"username":null,"session":null,"msg_type":"kernel_info_request","version":"5.2"},"metadata":{},"content":{},"buffers":[],"parent_header":{},"channel":"shell"}))

        ws.send(JSON.stringify({"header":{"msg_id":uuid(),"username":null,"session":null,"msg_type":"comm_info_request","version":"5.2"},"metadata":{},"content":{"target_name":"jupyter.widget"},"buffers":[],"parent_header":{},"channel":"shell"}));

        ws.send(JSON.stringify({"header":{"msg_id":uuid(),"username":null,"session":null,"msg_type":"execute_request","version":"5.2"},"metadata":{},"content":{"code":"a = 2","silent":false,"store_history":true,"user_expressions":{},"allow_stdin":true,"stop_on_error":true},"buffers":[],"parent_header":{},"channel":"shell"}));

        ws.send(JSON.stringify({"header":{"msg_id":uuid(),"username":null,"session":null,"msg_type":"execute_request","version":"5.2"},"metadata":{},"content":{"code":"print(a)","silent":false,"store_history":true,"user_expressions":{},"allow_stdin":true,"stop_on_error":true},"buffers":[],"parent_header":{},"channel":"shell"}));
        
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
            fetch('/api/kernels/' + k.id, {
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

