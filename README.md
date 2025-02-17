# py-playground

Python playground for miscelaneous ideas

```bash
./json2json.py -pp "attributes.[].abc" -pp "sub0" -x 10
regex_path: [regex.Regex('attributes\\.\\[[0-9]+\\]\\.abc.*', flags=regex.V0), regex.Regex('sub0.*', flags=regex.V0)]
{
  "a": 1,
  "b": 2,
  "c": 3,
  "attributes": [
    {
      "x": 1,
      "y": 2,
      "z": "value",
      "abc": {"a": 1, "b": 2}
    }
  ],
  "sub0": {"sub1": {"key1": "value1", "key2": "value2", "key3": "value3"}}
}
```

```bash
./json2json.py  -x 10                                  
regex_path: []
{
  "a": 1,
  "b": 2,
  "c": 3,
  "attributes": [
    {
      "x": 1,
      "y": 2,
      "z": "value",
      "abc": {
        "a": 1,
        "b": 2
      }
    }
  ],
  "sub0": {
    "sub1": {
      "key1": "value1",
      "key2": "value2",
      "key3": "value3"
    }
  }
}
```

```bash
./json2json.py  -x 1 
regex_path: []
{
  "a": 1,
  "b": 2,
  "c": 3,
  "attributes": [
    {"x": 1, "y": 2, "z": "value", "abc": {"a": 1, "b": 2}}
  ],
  "sub0": {
    "sub1": {"key1": "value1", "key2": "value2", "key3": "value3"}
  }
}
```
