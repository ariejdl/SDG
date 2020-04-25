const node_{sym} = new Node(
  {sym},
  () => [{dependencies}],

  () => [{dependents}],
  [{dependentAllowNulls}],
  () => [{dependentArgs}],

  function () {{
    {initBody}
  }},
  
  function (networkInvocationId{namedArgs}) {{
    {body}
  }}
)
