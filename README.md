# UAssetAPI (With BL3/WL Modding Enhancements)
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

3. Press F6 and right-click the solution name in the Solution Explorer and press "Build Solution" to compile UAssetAPI.

## Compilation, Linux

Compiling on Linux is pretty straightforward.  I did so using
[Mono](https://www.mono-project.com/) rather than
[dotnet](https://dotnet.microsoft.com/en-us/download).  I didn't
want to bother with that whole "NuGet" package management system,
so I manually downloaded the one dependency
[Newtonsoft.Json](https://github.com/JamesNK/Newtonsoft.Json/releases)
and put `Newtonsoft.Json.dll` right into the `UAssetAPI` dir (alongside
`UAssetAPI.csproj`.  I then modified the Newtonsoft stanza in
`UAssetAPI.csproj` to read:

```xml
<Reference Include="Newtonsoft.Json">
    <HintPath>Newtonsoft.Json.dll</HintPath>
</Reference>
```

Once that was done, the following will build a debug version:

    $ msbuild /p:Configuration=Debug UAssetAPI.csproj

... or for a Release version:

    $ msbuild /p:Configuration=Release UAssetAPI.csproj

That should create a `bin/Debug/UAssetAPI.dll` or
`bin/Release/UAssetAPI.dll` for you.

## Contributing
Any contributions, whether through pull requests or issues, that you make are greatly appreciated.

If you find an Unreal Engine 4 .uasset that has its `VerifyBinaryEquality()` method return false (or display "failed to maintain binary equality" within [UAssetGUI](https://github.com/atenfyr/UAssetGUI)), feel free to submit an issue here with a copy of the asset in question along with the name of the game and the Unreal version that it was cooked with and I will try to push a commit to make it verify parsing.

## License
UAssetAPI and UAssetGUI are distributed under the MIT license, which you can view in detail in the [LICENSE file](LICENSE).

## Changelog

This changelog is basically just for this BL3/WL-specific fork.

**2022-10-25-01** - Initial Release
 - Moved `StatementIndex` labels to the top of each statement,
   instead of the bottom
 - Added `_hotfix_index` labels inside serialized Ubergraph JSON

