let node_5_data = null;
const node_5_callable = (networkInvocationId) => {
  const _dependents = [node_8_data, node_9_data];
  const _dependentsAllowNulls = [false, false];
  const _dependentArgs = [[networkInvocationId, node_10_data, node_5_data], [networkInvocationId, node_10_data, node_5_data]];

  if (updateAndCheckCalls(networkInvocationId, 'node_5_callable')) {
    // in case there is too much recursion
    return;
  }

  // this is stateful, need to know previous values
  if (allowCallAndChanged(_nodeDepencies['node_5_callable'], [])) {
    _nodeDepencies['node_5_callable'] = [];

    node_5_data = null;

    for (let i = 0; i < dependendents.length; i++) {
      if (_dependentsAllowNulls[i] || arrayNoNulls(_dependentArgs[i])) {
        const res = _dependents[i]({ ..._dependentArgs[i] });
        // if (isPromise) { res.then( fn ); }
      }
    }
  }
}
let node_10_data = null;
const node_10_callable = (networkInvocationId) => {
  const _dependents = [node_7_data, node_6_data, node_8_data, node_9_data];
  const _dependentsAllowNulls = [false, false, false, false];
  const _dependentArgs = [[networkInvocationId, node_8_data], [networkInvocationId, node_10_data], [networkInvocationId, node_10_data, node_5_data], [networkInvocationId, node_10_data, node_5_data]];

  if (updateAndCheckCalls(networkInvocationId, 'node_10_callable')) {
    // in case there is too much recursion
    return;
  }

  // this is stateful, need to know previous values
  if (allowCallAndChanged(_nodeDepencies['node_10_callable'], [])) {
    _nodeDepencies['node_10_callable'] = [];

    node_10_data = null;

    for (let i = 0; i < dependendents.length; i++) {
      if (_dependentsAllowNulls[i] || arrayNoNulls(_dependentArgs[i])) {
        const res = _dependents[i]({ ..._dependentArgs[i] });
        // if (isPromise) { res.then( fn ); }
      }
    }
  }
}
{
              width: 200,
height: 200,
x_accessor: (v) => v[1],
y_accessor: (v) => v[2],
id_accessor: (v) => v[0]
            }let node_8_data = null;
const node_8_callable = (networkInvocationId, $conf, $data) => {
  const _dependents = [node_7_data];
  const _dependentsAllowNulls = [false];
  const _dependentArgs = [[networkInvocationId, node_8_data]];

  if (updateAndCheckCalls(networkInvocationId, 'node_8_callable')) {
    // in case there is too much recursion
    return;
  }

  // this is stateful, need to know previous values
  if (allowCallAndChanged(_nodeDepencies['node_8_callable'], [node_10_data, node_5_data])) {
    _nodeDepencies['node_8_callable'] = [node_10_data, node_5_data];

    node_8_data = d3.scaleLinear.domain([d3.min($data, $conf.x_accessor), d3.max($data, $conf.x_accessor)])
.range([0, $conf.width])
;

    for (let i = 0; i < dependendents.length; i++) {
      if (_dependentsAllowNulls[i] || arrayNoNulls(_dependentArgs[i])) {
        const res = _dependents[i]({ ..._dependentArgs[i] });
        // if (isPromise) { res.then( fn ); }
      }
    }
  }
}
let node_9_data = null;
const node_9_callable = (networkInvocationId, $conf, $data) => {
  const _dependents = [node_7_data];
  const _dependentsAllowNulls = [false];
  const _dependentArgs = [[networkInvocationId, node_8_data]];

  if (updateAndCheckCalls(networkInvocationId, 'node_9_callable')) {
    // in case there is too much recursion
    return;
  }

  // this is stateful, need to know previous values
  if (allowCallAndChanged(_nodeDepencies['node_9_callable'], [node_10_data, node_5_data])) {
    _nodeDepencies['node_9_callable'] = [node_10_data, node_5_data];

    node_9_data = d3.scaleLinear.domain([d3.min($data, $conf.y_accessor), d3.max($data, $conf.y_accessor)])
.range([0, $conf.height])
;

    for (let i = 0; i < dependendents.length; i++) {
      if (_dependentsAllowNulls[i] || arrayNoNulls(_dependentArgs[i])) {
        const res = _dependents[i]({ ..._dependentArgs[i] });
        // if (isPromise) { res.then( fn ); }
      }
    }
  }
}
