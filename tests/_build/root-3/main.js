
// notes:
// records dependencies of previous activation of node
// _nodeDependencies[] = {{}}

// record/track call stack so can prevent infinite loops, e.g. callStack.indexOf(node_sym_callback)...
// e.g. callCount = {{}} // every _callbable is called with the current resolution_id...cull after one second, mark last call count Date.now()
// e.g. callCount{{node_callbable}} += 1
// e.g. check recursion depth and stop

// what about async,throttling etc.?

// interactive UI creation could be accomplished with
// passing variables through network


// - ... recipes are similar to this ...
// - ... strongly desire to remove namespaces ... require $ prefix, thus $conf ... e.g. 'conf' ...
//       - ... very hard to refactor dependents ... loose coupling ...


const maxRecursion = 50;
let _networkInvocationId = 0;

let _nodeDepencies = {};

let _networkInvocations = {};
function updateAndCheckCalls(_networkInvocationId, callable) {
  // check excessive recursion
  let current = _networkInvocations[_networkInvocationId];
  if (current === undefined) {
    let obj = { _time: Date.now() };
    _networkInvocations[callable] = obj;
    obj[callable] = 1;
    return false;
  }

  if ((current._time + 1000) > Date.now()) {
    // reset after one second
    let obj = { _time: Date.now() };
    _networkInvocations[callable] = obj;
    obj[callable] = 1;
    return false;
  } else {
    const count = current[callable];
    current['_time'] = Date.now();
    if (count === undefined) {
      // have not seen this node
      current[callable] = 1;
      return false;
    } else if (count > maxRecursion) {
      // too much recursion
      throw "Too much recursion";
      return true;
    } else {
      // increment call count
      current[callable] = count + 1;
    }
  }

  return false;
}

// https://github.com/getify/TNG-Hooks
// NOTE: both `guards1` and `guards2` are either
//    `undefined` or an array
function guardsChanged(guards1,guards2) {
  // either guards list not set?
  if (guards1 === undefined || guards2 === undefined) {
    // force assumption of change in guards
    return true;
  }

  // guards lists of different length?
  if (guards1.length !== guards2.length) {
    // guards changed
    return true;
  }

  // check guards lists for differences
  //    (only shallow value comparisons)
  for (let [idx,guard] of guards1.entries()) {
    if (!Object.is(guard,guards2[idx])) {
      // guards changed
      return true;
    }
  }

  // assume no change in guards
  return false;
}


function allowCallAndChanged(prev, current) {
  return guardsChanged(prev, current);
}


function arrayNoNulls(arr) {
  for (let i = 0; i < arr.length; i++) {
    if (arr[i] === null || arr[i] === undefined) {
      return false;
    }
  }
  return true;
}
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
