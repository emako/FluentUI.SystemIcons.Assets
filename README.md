# Fluent UI System Icons Assets NuGet Package

This is a content-only NuGet package that contains the Fluent UI System Icons assets.

## Package Contents

The package includes the following icon assets:
- **FluentSystemIcons-Filled**: Filled style icons
- **FluentSystemIcons-Light**: Light style icons
- **FluentSystemIcons-Regular**: Regular style icons
- **FluentSystemIcons-Color**: Color style icons

Each icon is available in multiple formats and sizes for different use cases.

## Installation

Install the NuGet package from the Package Manager:

```xml
<PackageReference Include="FluentUI.SystemIcons.Assets" Version="1.1.323" />
```

Or via Package Manager Console:

```powershell
Install-Package FluentUI.SystemIcons.Assets
```

## Usage

After installing the package, the icon assets will be available in the `assets` folder of your project:

```
packages/FluentUI.SystemIcons.Assets/assets/
├── FluentSystemIcons-Filled/
├── FluentSystemIcons-Light/
├── FluentSystemIcons-Regular/
└── FluentSystemIcons-Color/
```

## Building the Package

To build this NuGet package from the nuspec file:

```powershell
.\build_nuget.ps1
```

The package will be generated in the current directory.

## License

This package is licensed under the MIT License. See the LICENSE file in the fluentui-system-icons repository for details.

## Resources

- [Fluent UI System Icons Repository](https://github.com/microsoft/fluentui-system-icons)
- [NuGet Package Page](https://www.nuget.org/packages/FluentUI.SystemIcons.Assets/)
