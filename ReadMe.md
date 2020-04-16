# Read Me

## Development

`pip install -e .`

Longer term thoughts: would be nice to have server and client written in typescript could then share code on front-end and back-end.  For example could then generate code in client...drawback is not having nice Python libraries and easier syntax

## Tests

`pytest tests [-s]`

## front-end

```
cd client
./node_modules/webpack/bin/webpack.js [--watch] [--env.production]
```

comes from: <https://github.com/Microsoft/TypeScript-Babel-Starter#readme>

# MVP:

- static server
- csv file sent down
- data bound to a chart

this needs:
- need to be able to keep existing server and/or client running while make changes
  - rebuild parts of the network independently, only the parts that have changed
  - e.g. keep serving a csv file while change the visual and rebuild the UI
- well specified 'make' step, e.g. emit code to specified directory
  - emit code into temp directory
- well specified 'run' step, i.e. start server, inform UI, want to be able to restart the UI and keep running this
  - subprocess with boilerplate to communicate asynchronously with this parent process