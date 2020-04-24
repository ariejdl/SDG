const node_{sym} = new Node(
  {sym},
  () => [{dependencies}],

  () => [{dependents}],
  [{dependentAllowNulls}],
  () => [{dependentArgs}],

  {initBody},
  
  (networkInvocationId{namedArgs}) => {{
    this.data = {body};
  }}
)
