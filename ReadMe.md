# Read Me

Save time in data-visualisation and software development, particular web software application development.  Influenced by the principles of visual basic, and popular approaches in data visualisation SDG tries to simplify programming.

## Development

`pip install -e .`

Longer term thought: the server is written in Python rather than Typescript partly because jupyter_client is in use.

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

#### Footnotes

SDG: Soli Deo Gloria latin for "glory to God alone", a reformation maxim.  "The fear of the Lord is the beginning of wisdom", Proverbs 9:10.