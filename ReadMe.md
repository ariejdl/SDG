# Read Me

## Development

`pip install -e .`

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
- data bound to bar chart; good implementation is probably a javascript 'pivot' (edge)

this needs:
- well specified 'make' step, e.g. emit code to specified directory
  - emit code into temp directory
- well specified 'run' step, i.e. start server, inform UI, want to be able to restart the UI and keep running this
  - subprocess with boilerplate to communicate asynchronously with this parent process