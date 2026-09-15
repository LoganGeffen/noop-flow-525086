# Noop flow reference

[Published page](https://logangeffen.github.io/noop-flow-525086/)

Edit the prose in `page.template.html` and the figures in `diagrams/`, then run
`python3 build.py` to regenerate the self-contained `index.html` served by Pages.
The build uses Python 3 with `lxml` and D2 (verified with v0.7.1).

`build.py` pins repository links to the reviewed CannamatrixAI revision. It links
only source-path text inside the diagrams. Update that revision only after
checking the diagrams against the new source.
