# UAssetAPI (With BL3/WL Modding Enhancements)

- [Overview](#overview)
- [Compilation, Windows](#compilation-windows)
  - [Prerequisites](#prerequisites)
  - [Initial Setup](#initial-setup)
- [Compilation, Linux](#compilation-linux)
- [Ancillary Scripts](#ancillary-scripts)
  - [CLI Serialization](#cli-serialization)
  - [Graphing](#graphing)
- [Contributing](#contributing)
- [License](#license)
- [Changelog](#changelog)

## Overview
A .NET library for reading and writing Unreal Engine 4 game assets.

This fork includes some enhancements to make ubergraph bytecode
serialization more useful to people writing [hotfix mods for
Borderlands 3](https://borderlandsmodding.com/bl3-writing-mods/)
and [Tiny Tina's Wonderlands](https://borderlandsmodding.com/wl-writing-mods/).

Specifically, Gearbox uses a "hotfix" system to deliver small
tweaks and updates to the game, without having to patch the game
data, and the hotfix modding community makes use of that to write
our own mods.  One hotfix type that BL3 and WL support is [editing
Ubergraph Bytecode literals](https://github.com/BLCM/BLCMods/wiki/Borderlands-3-Hotfixes#hotfix-type-7-blueprint-bytecode),
and UAssetAPI/UAssetGUI gives us a great way to see what the
bytecode is doing, and provide us with the offsets we need to
specify in the hotfixes.

So, the primary reason for this fork is to add in `_hotfix_index`
keys to the serialized bytecode JSON, in front of all the values
which we're capable of hotfixing.  For instance, one stanza from a
Wonderlands ubergraph comes out like:

```json
"Expression": {
  "Inst": "CallMath",
  "Function": "FClamp",
  "ContextClass": "/Script/Engine.KismetMathLibrary",
  "Parameters": [
    {
      "Inst": "LocalVariable",
      "Variable Outer": "Init_EnchantmentWeight_C",
      "Variable Name": "CalculateAttributeInitialValue.CallFunc_Multiply_FloatFloat_ReturnValue"
    },
    {
      "Inst": "FloatConst",
      "_hotfix_index": 504,
      "Value": 0.1
    },
    {
      "Inst": "FloatConst",
      "_hotfix_index": 509,
      "Value": 0.35
    }
  ]
}
```

The two values we can change there are the two parameters to the `FClamp`
call, and we'd use index 504 and/or 509 to do so, in the hotfix.

The opcode types that we're capable of editing using this method are:
 - ByteConst
 - False
 - FloatConst
 - InstanceDelegate
 - Int64Const
 - IntConst
 - IntConstByte
 - IntOne
 - IntZero
 - NameConst
 - ObjectConst
 - RotationConst
 - TransformConst
 - True
 - UInt64Const
 - VectorConst

This fork also moves the `StatementIndex` keys up to the top of each
statement, just for ease of human readability.

To make use of it, either compile it yourself (see below) or grab a
precompiled DLL from the Releases area.  Slap `UAssetAPI.dll` into
UAssetGUI's dir, or wherever you need it for API access to work.

<img src="https://i.imgur.com/GZbr93m.png" align="center">

## Compilation, Windows
If you'd like to compile UAssetAPI for yourself, read on:

### Prerequisites
* Visual Studio 2017 or later
* Git

### Initial Setup
1. Clone the UAssetAPI repository:

```sh
git clone https://github.com/atenfyr/UAssetAPI.git
```

2. Open the `UAssetAPI.sln` solution file within the newly-created UAssetAPI directory in Visual Studio, right-click on the solution name in the Solution Explorer, and press "Restore Nuget Packages."

3. Press F6 or right-click the solution name in the Solution Explorer and press "Build Solution" to compile UAssetAPI. Note that this solution does not include UAssetGUI.

## Compilation, Linux
Compiling on Linux is pretty straightforward.  I did so using
[Mono](https://www.mono-project.com/) rather than
[dotnet](https://dotnet.microsoft.com/en-us/download).  Note that this
project does make use of the "NuGet" package management system.  I'd
originally resisted that a bit, but that's become more trouble than
it's worth.

To restore all the NuGet dependencies at the same time as building, the
following will build a debug version:

    $ msbuild -r -t:Publish -p:Configuration=Debug UAssetAPI.csproj

... or for a Release version:

    $ msbuild -r -t:Publish -p:Configuration=Release UAssetAPI.csproj

That should create a `bin/Debug/netstandard2.0/publish/UAssetAPI.dll` or
`bin/Release/netstandard2.0/publish/UAssetAPI.dll` for you.  The `-t:Publish`
argument is important because that's what copies `Newtonsoft.Json.dll` into
place in the build directory.  Depending on your Mono config, you might see
a target other than `netstandard2.0` in there.

To skip the NuGet dependency steps, omit `-r`, but note that you'll have
to restore at least once, using:

    $ msbuild -t:Restore UAssetAPI.csproj

I've wrapped up this functionality into a few shell scripts at the project
root, namely `build-restore.sh`, `build-debug.sh`, and `build-release.sh`.

## Ancillary Scripts
This fork also provides a couple of [Python](https://www.python.org) scripts
to help out with a couple of tasks useful for getting a grip on bytecode
serializations.  The first is to provide a handy way to trigger bytecode
serializations from the CLI, and the other is to generate some
[Graphviz](https://graphviz.org/) "dot" graphs of the serialized bytecode.

Both scripts are found in the `scripts` directory in the git tree, or in
the zipfiles in the "Releases" section.  They should both be runnable in-place
from the unzipped release file, or directly from the git checkout, so long
as UAssetAPI has been compiled.  On Linux systems, you should be able to
symlink them into your `~/bin` directory or wherever you'd like.

### CLI Serialization
The first script, `serialize-ubergraph.py`, can be used to generate
ubergraph bytecode serializations of the given UE4 object (`.uasset` or
`.umap`).  The script is actually extremely forgiving with specifying the
filename, to make tab-completion easier.  You can provide just the "base"
filename (without any extension), just a single `.` at the end, or any
extension fragment like `.u` (common when tab-completing since there's
generally a `.uasset` and `.uexp` file sitting side-by-side).

This script *requires* [Python.NET](http://pythonnet.github.io/)
([github](https://github.com/pythonnet/pythonnet), [pypi](https://pypi.org/project/pythonnet/)),
so be sure to do a `pip install pythonnet` to get it installed first
(or install it with your distro's package manager).

The syntax is pretty basic:

    $ serialize-ubergraph.py --help
    usage: serialize-ubergraph.py [-h] [-r] filename

    Serialize Ubergraph Bytecode using UAssetAPI

    positional arguments:
      filename       Filename to process

    options:
      -h, --help     show this help message and exit
      -r, --raw   Also save out raw bytecode
	  --runtime   Show .NET runtime being used

And, as an example:

    $ serialize-ubergraph.py Passive_Rogue_13.u
    Loading UAssetAPI.dll from: /home/pez/UAssetAPI-2022-11-23-01
    Wrote to: Passive_Rogue_13-ubergraph-005-ExecuteUbergraph_Passive_Rogue_13.json
    Wrote to: Passive_Rogue_13-ubergraph-006-OnActivated.json
    Wrote to: Passive_Rogue_13-ubergraph-007-OnDeactivated.json

If the script isn't automatically finding the `UAssetAPI.dll` file to use, you can
hardcode its location up near the top of the script.

Passing in the `-r` or `--raw` options will have it also save out the raw bytecode
in a `.raw` file alongside the JSON serializations.  Note that that does *not*
match the in-memory bytecode; as it's loaded in, various things get converted to
pointers, instead of the on-disk indexes.

### Graphing
The next script, `bytecode-to-dot.py`, is used to create some
[Graphviz](https://graphviz.org) "dot" graphs of the serialized bytecode.  It
operates on the JSON files generated by `serialize-ubergraph.py`.  It's a *bit*
silly to have it process those instead of using UAssetAPI directly, but I
nearly always want on-disk JSON serializations anyway, so for my own workflow
it's more convenient to generate those first and then build graphs off of them.

This script doesn't require anything but stock Python libraries, but it *does*
require that Graphviz's `dot` executable is available on your system path to do
the rendering.  (Otherwise it'll just generate a `.dot` file and leave it to you
to render it however you like.)  As an example of the sort of graph it can
generate:

![Bytecode Graph](https://raw.githubusercontent.com/apocalyptech/UAssetAPI/master/graph.png)

The `StatementIndex` of each statement is included in angle brackets in front of the
bold opcode type, on the first line of each node.  From that point on, whenever
a hotfixable bit of data is encountered, it should prefix it with a square-bracketed
index.  For instance, in that example graph, the only two hotfixable values are
the `True` at index 159, and the `False` at index 42.

Its syntax is pretty basic:

    $ bytecode-to-dot.py --help
    usage: bytecode-to-dot.py [-h] [-r {png,svg,none}] [-d DISPLAY] [--no-display] filename

    Represent Ubergraph bytecode scripts as dotfiles

    positional arguments:
      filename              JSON filename to process

    options:
      -h, --help            show this help message and exit
      -r {png,svg,none}, --render {png,svg,none}
                            Render type
      -d DISPLAY, --display DISPLAY
                            Application to use to display renders
      --no-display          Don't auto-display renders

By default it'll try to render the dotfile as an SVG, but you can specify `-r png` to
generate a PNG, or `none` to turn off rendering altogether.  If rendering an SVG or
PNG, it'll also attempt to display the render immediately after generation, unless
you specify `--no-display`.  The application used to open them can be specified with
`-d`/`--display`, and defaults to [feh](https://feh.finalrewind.org/).

Like the serialization script, it's pretty forgiving about the filename given in
the arguments, to make tab-completions easier:

    $ bytecode-to-dot.py Passive_Rogue_13-ubergraph-005-ExecuteUbergraph_Passive_Rogue_13.
    Generated: Passive_Rogue_13-ubergraph-005-ExecuteUbergraph_Passive_Rogue_13.dot
    Rendered to: Passive_Rogue_13-ubergraph-005-ExecuteUbergraph_Passive_Rogue_13.svg

Note that there are various opcodes which haven't really been tested, since I
haven't yet run into them on the data I'm looking at.  You may see some messages
printed on the console if you generate graphs which contain any of those.  Let
me know if they look funky!  Also, there's a few more complex-looking opcodes which
I'm not doing *any* custom processing on -- in the graphs, they'll basically just
tell you what sort of opcode they are and not show any detail.  If you come across
examples of those, I'd appreciate sending the data over so I can see how to
get them displayed.

The full list of opcodes that I'm not doing custom processing on is:
 - Assert
 - InstrumentaionEvent
 - MapConst
 - SetConst
 - SetMap
 - SetSet

## Contributing
Any contributions, whether through pull requests or issues, that you make are greatly appreciated.

If you find an Unreal Engine 4 .uasset that has its `VerifyBinaryEquality()` method return false (or display "failed to maintain binary equality" within [UAssetGUI](https://github.com/atenfyr/UAssetGUI)), feel free to submit an issue here with a copy of the asset in question along with the name of the game and the Unreal version that it was cooked with and I will try to push a commit to make it verify parsing.

## License
UAssetAPI and UAssetGUI are distributed under the MIT license, which you can view in detail in the [LICENSE file](LICENSE).

## Changelog
This changelog is basically just for this BL3/WL-specific fork.

*(unreleased)*
 - Added graphing support for `CallMulticastDelegate` opcodes (though the
   `Parameters` array in there is basically still untested, except for cases
   where it's empty)

**2022-11-23-01**
 - When a `StructConst` of type `/Script/CoreUObject.Guid` is detected, will
   add an `_interpreted_guid` to the serialization, which will match the GUIDs
   seen while serializing objects with JWP, etc.
 - Default to SVG rendering in `bytecode-to-dot.py`, instead of PNG
 - Merged in some commits from upstream (including various packaging/building
   changes)
 - Report on which `UAssetAPI.dll` is being used, in `serialize-ubergraph.py`

**2022-11-02-01**
 - Added `--raw` option to `serialize-ubergraph.py` to save out raw on-disk
   bytecode alongside serializations
 - `StructExport` will always include raw serialization, instead of only doing
   so when serialization errors occur
 - Merged in some commits from upstream
 - `bytecode-to-dot.py` will use angled brackets instead of square brackets to
   report the "main" statement bytecode index (to prevent confusion with the
   actually-hotfixable statements, which use square brackets)

**2022-10-25-02**
 - Added serialization and graphing scripts
 - Include README and Licenses in distributed zip
 - Checked in my own build scripts
 - Merged in a bugfix from upstream

**2022-10-25-01**
 - Initial Release
 - Moved `StatementIndex` labels to the top of each statement,
   instead of the bottom
 - Added `_hotfix_index` labels inside serialized Ubergraph JSON

