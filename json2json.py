#!/usr/bin/env -S python
"""
Load JSON and dump it so the output is compact but not too compact.
Which in general mean that should print all the elements at either:
- certain depth as compact
- certain path as compact
"""

import json
import configargparse
from typing import List
import regex as re

DEF_MAX_DEPTH = -1
DEF_INDENT = 2
DEF_CONFIG_PATHS = [
    "/etc/archiv.conf",
    "/etc/archiv.d/*.conf",
    "~/.config/archiv/wui.conf",
]


def parse_args() -> configargparse.Namespace:
    """Parse arguments"""
    p = configargparse.ArgParser(
        "json2json",
        config_file_parser_class=configargparse.YAMLConfigFileParser,
        default_config_files=DEF_CONFIG_PATHS,
    )
    p.add_argument(
        "-c",
        "--app-config",
        required=False,
        is_config_file=True,
        help="config file path",
    )
    p.add_argument("-i", "--indent", type=int, default=DEF_INDENT)
    p.add_argument("-x", "--max-depth", type=int, default=DEF_MAX_DEPTH)
    p.add_argument(
        "-rp",
        "--regex-path",
        action="append",
        type=str,
        help="Regular expression to match path (be careful with special characters)",
        required=False,
    )
    p.add_argument(
        "-pp",
        "--path-prefix",
        action="append",
        type=str,
        help="dotted path prefix to match path (e.g. 'a.b.c.'), gets converted to regex",
        required=False,
    )
    p.add_argument(
        "-f", "--form", type=str, choices=["plain", "ansi", "html"], default="ansi"
    )
    p.add_argument("--no-extra-spaces", action="store_true")
    p.add_argument("-o", "--output", type=str, default=None)
    p.add_argument("file", type=str, nargs="?")
    return p.parse_args()


class Json2Json:
    """Convert JSON to JSON"""

    def __init__(self, args: configargparse.Namespace):
        self.args = args
        if args.regex_path is None:
            args.regex_path = []
        else:
            args.regex_path = [re.compile(p) for p in args.regex_path]
        if args.path_prefix is not None:
            for pp in args.path_prefix:
                pp = pp.replace(".", r"\.")
                pp = pp.replace("*", r".*")
                pp = pp.replace("[]", r"\[[0-9]+\]")
                args.regex_path += [re.compile(f"{pp}.*")]
        print(f"regex_path: {args.regex_path}")

    def run_file(self):
        with open(self.args.file, "r") as f:
            data = json.load(f)
        self.run_data(data)

    def run_data(self, data):
        if self.args.output:
            with open(self.args.output, "w") as f:
                f.write(self.dump(data, indent=self.args.indent, depth=0))
        else:
            print(self.dump(data, indent=self.args.indent, depth=0))

    def compact_list(self, data, indent, depth, path):
        return (
            "["
            + ",".join(
                self.dump(
                    list_el,
                    indent=indent,
                    depth=depth + 1,
                    path=path + [f"[{str(idx)}]"],
                )
                for idx, list_el in enumerate(data)
            )
            + "]"
        )

    def indented_list(self, data, indent, depth, path):
        return (
            "["
            + ",".join(
                f"\n{' '*indent*(depth+1)}{self.dump(list_el, indent=indent, depth=depth+1,path=path + [f'[{str(idx)}]'])}"
                for idx, list_el in enumerate(data)
            )
            + f"\n{' '*indent*depth}"
            + "]"
        )

    def compact_dict(self, data, indent, depth, path):
        return (
            "{"
            + f",{'' if self.args.no_extra_spaces else ' '}".join(
                f'"{kk}":{"" if self.args.no_extra_spaces else " "}{self.dump(vv,indent=indent,depth=depth+1,path=path + [str(kk)])}'
                for kk, vv in data.items()
            )
            + "}"
        )

    def indented_dict(self, data, indent, depth, path):
        return (
            "{"
            + ",".join(
                f"\n{' '*indent*(depth+1)}\"{kk}\":{'' if self.args.no_extra_spaces else ' '}{self.dump(vv,indent=indent,depth=depth+1,path=path + [str(kk)])}"
                for kk, vv in data.items()
            )
            + f"\n{' '*indent*depth}"
            + "}"
        )

    def dump(self, obj, indent=None, depth=0, path: List[str] = []):
        # dump elementary types int,str,bool,None,float
        path_str = ".".join(path)
        if isinstance(obj, (int, str, bool, type(None), float)):
            # debug:
            # return f"**{path_str}**" + json.dumps(obj)
            return json.dumps(obj)
        if isinstance(obj, list) or isinstance(obj, tuple):
            if self.args.regex_path is not None and len(self.args.regex_path) > 0:
                if any(re.match(p, path_str) for p in self.args.regex_path):
                    return self.compact_list(obj, indent, depth, path)
                return self.indented_list(obj, indent, depth, path)
            else:
                if depth > self.args.max_depth:
                    return self.compact_list(obj, indent, depth, path)
                return self.indented_list(obj, indent, depth, path)
        if isinstance(obj, dict):
            if self.args.regex_path is not None and len(self.args.regex_path) > 0:
                if any(re.match(p, path_str) for p in self.args.regex_path):
                    return self.compact_dict(obj, indent, depth, path)
                return self.indented_dict(obj, indent, depth, path)
            else:
                if depth > self.args.max_depth:
                    return self.compact_dict(obj, indent, depth, path)
                return self.indented_dict(obj, indent, depth, path)


def test() -> None:
    """Test function"""
    vala = {
        "a": 1,
        "b": 2,
        "c": 3,
        "attributes": [{"x": 1, "y": 2, "z": "value", "abc": {"a": 1, "b": 2}}],
        "sub0": {"sub1": {"key1": "value1", "key2": "value2", "key3": "value3"}},
    }
    dumper = Json2Json(parse_args())
    dumper.run_data(vala)


if __name__ == "__main__":
    cli_args = parse_args()
    if cli_args.file:
        dumper = Json2Json(cli_args)
        dumper.run_file()
    else:
        test()
