let node_{sym}_data = {initBody};
const node_{sym}_callable = (networkInvocationId{namedArgs}) => {{
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
