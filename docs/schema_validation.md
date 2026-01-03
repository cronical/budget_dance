# Schema validation

The tooling options are pretty confusing.

To validate the schema itself I found that `ajv` is the best [documented](https://github.com/ajv-validator/ajv-cli) and works well.

To install:

```commandline
homebrew install node
npm install 
npm install -g ajv-cli
```

The following line validates the schema.

```
$ ajv compile -s dance/book/setup_schema.json --spec=draft2020 --allow-union-types
schema dance/book/setup_schema.json is valid
```
