
// records dependencies of previous activation of node
// _nodeDependencies[] = {}

// record/track call stack so can prevent infinite loops, e.g. callStack.indexOf(node_sym_callback)...
// e.g. callCount = {} // every _callbable is called with the current resolution_id...cull after one second, mark last call count Date.now()
// e.g. callCount{node_callbable} += 1
// e.g. check recursion depth and stop

// what about async,throttling etc.?

// real time updates could be accomplished with
// 1) passing variables through graph that are interactively updated
// 2) cached compilation

let node_{sym}_data = {initBody};
const node_{sym}_callable = (network_invocation_id, {args}) => {
    const _dependents = {dependents};
    const _dependentsAllowNulls = {dependentAllowNulls};
    const _childArgs = {childArgs};

    if (updateAndCheckCalls(network_invocation_id, node_{sym}_data)) {
        // in case there is too much recursion
        return;
    }

    // this is stateful, need to know previous values
    if (allowCallAndChanged(_nodeDepencies[node_{sym}_callable], {dependencies})) {
        _nodeDepencies[node_{sym}_callable] = {dependencies};

        node_{sym}_data = {body};

        for (let i = 0; i < dependendents.length; i++) {
            if (_dependentsAllowNulls[i] || objNoNulls(childArgs[i])) {
                const fn = _dependents[i]({ ..._childArgs[i] });
                // if (isPromise) { ....then( fn ); }
            }
        }
    }

}

// - ... recipes are similar to this ...
// - ... strongly desire to remove namespaces ... require $ prefix, thus $conf ... e.g. 'conf' ...
//       - ... very hard to refactor dependents ... loose coupling ...
