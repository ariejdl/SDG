
// records dependencies of previous activation of node
// _nodeDependencies[] = {{}}

// record/track call stack so can prevent infinite loops, e.g. callStack.indexOf(node_sym_callback)...
// e.g. callCount = {{}} // every _callbable is called with the current resolution_id...cull after one second, mark last call count Date.now()
// e.g. callCount{{node_callbable}} += 1
// e.g. check recursion depth and stop

// what about async,throttling etc.?

// interactive UI creation could be accomplished with
// passing variables through network

let node_{sym}_data = {initBody};
const node_{sym}_callable = (networkInvocationId, {namedArgs}) => {{
  const _dependents = [{dependents}];
  const _dependentsAllowNulls = [{dependentAllowNulls}];
  const _dependentArgs = [{dependentArgs}];

  if (updateAndCheckCalls(networkInvocationId, 'node_{sym}_callable')) {{
    // in case there is too much recursion
    return;
  }}

  // this is stateful, need to know previous values
  if (allowCallAndChanged(_nodeDepencies['node_{sym}_callable'], [{dependencies}])) {{
    _nodeDepencies['node_{sym}_callable'] = [{dependencies}];

    node_{sym}_data = {body};

    for (let i = 0; i < dependendents.length; i++) {{
      if (_dependentsAllowNulls[i] || arrayNoNulls(_dependentArgs[i])) {{
        const res = _dependents[i]({{ ..._dependentArgs[i] }});
        // if (isPromise) {{ res.then( fn ); }}
      }}
    }}
  }}

}}

// - ... recipes are similar to this ...
// - ... strongly desire to remove namespaces ... require $ prefix, thus $conf ... e.g. 'conf' ...
//       - ... very hard to refactor dependents ... loose coupling ...
