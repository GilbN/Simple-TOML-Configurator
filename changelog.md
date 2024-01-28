# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog],
and this project adheres to [Semantic Versioning].

## [Unreleased]

- /

## [1.1.0] - 2024-01-28

## New Release: v1.1.0 - True Nested Configuration Support with Attribute Access

This release introduces a significant new feature: Nested Configuration Support with Attribute Access.

### What's New

**Nested Configuration Support with Attribute Access:** In previous versions, accessing and updating nested configuration values required dictionary-style access. With this release, we've made it easier and more intuitive to work with nested configuration values. Now, you can access and update these values using attribute-style access, similar to how you would interact with properties of an object in JavaScript.

Here's an example:

```python
# Access nested configuration values
print(settings.mysql.databases.prod)  # Output: 'db1'
settings.mysql.databases.prod = 'new_value'
settings.update()
print(settings.mysql.databases.prod)  # Output: 'new_value'
```

## [1.0.0] - 2023-08-27

- initial release

<!-- Links -->
[keep a changelog]: https://keepachangelog.com/en/1.0.0/
[semantic versioning]: https://semver.org/spec/v2.0.0.html

<!-- Versions -->
[unreleased]: https://github.com/gilbn/simple-toml-configurator/compare/1.1.0...HEAD
[1.1.0]: https://github.com/gilbn/simple-toml-configurator/releases/tag/1.1.0
[1.0.0]: https://github.com/gilbn/simple-toml-configurator/releases/tag/1.0.0