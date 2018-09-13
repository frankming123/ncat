# ncat
It is ncat implemented by myself

## usage

```usage
usage: ncat [-h] {client,server} ...

ncat python version

positional arguments:
  {client,server}  sub-command help
    client         make nc as client
    server         make nc as server

optional arguments:
  -h, --help       show this help message and exit
```

## example

make it as tcp servser:

```command
python ncat.py server 127.0.0.1 8080
```

make it as udp client:

```command
python ncat.py client -u 127.0.0.1 8080
```

## License

MIT
