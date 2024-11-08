# Welcome to dj-data-generator Documentation!

[![License](https://img.shields.io/github/license/lazarus-org/dj-data-generator)](https://github.com/lazarus-org/dj-data-generator/blob/main/LICENSE)
[![PyPI Release](https://img.shields.io/pypi/v/dj-data-generator)](https://pypi.org/project/dj-data-generator/)
[![Pylint Score](https://img.shields.io/badge/pylint-10/10-brightgreen?logo=python&logoColor=blue)](https://www.pylint.org/)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/dj-data-generator)](https://pypi.org/project/dj-data-generator/)
[![Supported Django Versions](https://img.shields.io/pypi/djversions/dj-data-generator)](https://pypi.org/project/dj-data-generator/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=yellow)](https://github.com/pre-commit/pre-commit)
[![Open Issues](https://img.shields.io/github/issues/lazarus-org/dj-data-generator)](https://github.com/lazarus-org/dj-data-generator/issues)
[![Last Commit](https://img.shields.io/github/last-commit/lazarus-org/dj-data-generator)](https://github.com/lazarus-org/dj-data-generator/commits/main)
[![Languages](https://img.shields.io/github/languages/top/lazarus-org/dj-data-generator)](https://github.com/lazarus-org/dj-data-generator)
[![Coverage](https://codecov.io/gh/lazarus-org/dj-data-generator/branch/main/graph/badge.svg)](https://codecov.io/gh/lazarus-org/dj-data-generator)

[`dj-data-generator`](https://github.com/lazarus-org/dj-data-generator/) is a powerful Django package designed to facilitate realistic data generation for testing and development purposes. Developed to support large-scale data needs, it allows developers to populate database tables with customizable, constraint-aware, and highly representative sample data directly within their Django projects.

The package enables the generation of data across various fields, including integers, strings, dates, emails, IP addresses, and more, with careful attention to unique constraints, data types, and field limits. It also supports related models and nested relationships, ensuring consistency across complex data structures. With its flexibility, memory efficiency, and ability to handle large datasets, `dj-data-generator` is ideal for developers looking to streamline testing with accurate and varied data scenarios in Django applications.

## Project Detail

- Language: Python >= 3.9
- Framework: Django >= 4.2

## Documentation Overview

The documentation is organized into the following sections:

- **[Quick Start](#quick-start)**: Get up and running quickly with basic setup instructions.
- **[Usage](#usage)**: How to effectively use the package in your projects.
- **[Settings](#settings)**: Configuration options and settings you can customize.


---

# Quick Start

This section provides a fast and easy guide to getting the `dj-data-generator` package up and running in your Django project. Follow the steps below to quickly set up the package and start using it.

### 1. Install the Package

**Option 1: Using `pip` (Recommended)**

Install the package via pip:

```bash
$ pip install dj-data-generator
```
**Option 2: Using `Poetry`**

If you're using Poetry, add the package with:

```bash
$ poetry add dj-data-generator
```

**Option 3: Using `pipenv`**

If you're using pipenv, install the package with:

```bash
$ pipenv install dj-data-generator
```

### 2. Add to Installed Apps

After installing the necessary packages, ensure that `data_generator` is added to the `INSTALLED_APPS` in your Django ``settings.py`` file:

```python
INSTALLED_APPS = [
   # ...
   "data_generator",
   # ...
]
```

### 6. Generate Fake Data

After setting up the package, run the `generate_data` management command to generate fake data for project models

First, generate the audiences using the ``generate_audiences`` command:

```shell
$ python manage.py generate_data --num-records=1000
```

you can also use the `--skip-confirmation` argument to bypass the user confirmation prompt.

To generate fake data for a specific model, use the `--model=app.Model` argument.

----

# Usage
This section provides a comprehensive guide on how to utilize the package's key features.

## generate_data Command

The ``generate_data`` command generates fake data for all models in your Django project or for a specified model. It offers options to customize record count, skip confirmation prompts, and filter models and apps based on configuration settings.

### Command Overview

The ``generate_data`` command creates a specified number of records for each model, excluding some internal Django models by default (`admin.LogEntry`, `auth.Permission`, `contenttypes.ContentType`, `sessions.Session`) and any models or apps specified in the configuration. This is especially useful for populating your database with sample data for testing and development.

### Settings

This command is influenced by the following settings for fine-grained control over data generation:

- ``DATA_GENERATOR_EXCLUDE_APPS``:
  A list of app labels to exclude from data generation. Models within these apps will not be included in the data generation process.

- ``DATA_GENERATOR_EXCLUDE_MODELS``:
  A list of models to exclude from data generation, specified in the format app_label.ModelName. Any models listed here will be skipped.

- ``DATA_GENERATOR_CUSTOM_FIELD_VALUES``:
  Allows setting custom values for specific fields in specified models. This dictionary should have keys in the format `app_label.ModelName`, with each key containing a dictionary of field-value pairs to customize.

**Example**:
```python
DATA_GENERATOR_CUSTOM_FIELD_VALUES = {
    "auth.User": {
        "first_name": "sample",
        "email": "sample@example.com"
    }
}
```

### Usage

The command can be run using Django's ``manage.py`` utility:

```bash
$ python manage.py generate_data
```

### Optional Arguments

- ``--num-records``:
  Sets the number of records to generate per model. If not specified, the default is 100 records per model.

Example:
```shell
$ python manage.py generate_data --num-records 1000
```

- ``--skip-confirmation``:
  Skips the confirmation prompt, proceeding directly with data generation. Useful for automation or non-interactive environments.

Example:

```bash
$ python manage.py generate_audiences --skip-confirmation
```

- ``model``:
  Specifies a single model (in ``app_label.ModelName`` format) to generate data for, instead of generating data for all models.

Example:
```shell
$ python manage.py generate_data --model auth.User
```

### Command Flow

1. **Identify Target Models**:
   The command identifies all models, excluding those defined in ``DATA_GENERATOR_EXCLUDE_APPS`` and ``DATA_GENERATOR_EXCLUDE_MODELS``. If a specific model is specified with ``--model``, only that model will be targeted.

2. **Confirmation Prompt**:
   If no ``--skip-confirmation`` flag is set, the command lists the models to be processed and asks for user confirmation. This allows users to verify the list before proceeding with data generation.

3. **Generate Data for Models**:
   The command generates the specified number of records per model, handling unique fields and relationships between models. Related model instances are cached for reuse within a session.

4. **Output Progress**:
  A progress bar is displayed in the terminal, showing the completion percentage for each model.

### Example Output

When running the command, you may see output similar to:

```text
The following models were found:
1. <class 'django.contrib.auth.models.User'>
2. <class 'test_app.models.Profile'>
3. <class 'test_app.models.Order'>

Are these the correct target models?
 Type 'y' to proceed or 'n' to cancel the operation:y

Generating data for model: User
[ █ █ █ █ █ █ ─ ─ ─ ─ ] 60% completed for User

Generating data for model: Profile
[ █ █ █ █ █ █ █ █ █ █ ] 100% completed for Profile

Done!

```

----

# Settings

This section outlines the available settings for configuring the `dj-data-generator` package. You can customize these settings in your Django project's `settings.py` file to tailor the behavior of the data generator to your needs.

## Example Settings

Below is an example configuration with default values:

```python
DATA_GENERATOR_EXCLUDE_APPS = []
DATA_GENERATOR_EXCLUDE_MODELS = []
DATA_GENERATOR_CUSTOM_FIELD_VALUES = {}
```

## Settings Overview

Below is a detailed description of each setting, so you can better understand and tweak them to fit your project's needs.

### ``DATA_GENERATOR_EXCLUDE_APPS``

**Type**: ``list``

**Default**: ``[]`` (empty list)

**Description**: Specifies a list of app labels that should be excluded when running the `generate_data` command. If certain apps should not be considered for audience generation, list them here. For example:

```python

DATA_GENERATOR_EXCLUDE_APPS = ["finance", "store"]
```

This setting prevents the `generate_data` command from scanning the specified apps when generating fake data for models.

---

### ``DATA_GENERATOR_EXCLUDE_MODELS``

**Type**: ``list``

**Default**: ``[]`` (empty list)

**Description**: Specifies a list of model names that should be excluded when running the generate_data command. If certain models should not be included in the data generation process, define them here. For example:

```python
DATA_GENERATOR_EXCLUDE_MODELS = ["app_label.CustomModel", "app_label.AnotherModel"]
```

This setting allows fine-tuned control over which models are excluded from fake data creation, even if their app is not fully excluded.

---

### ``DATA_GENERATOR_CUSTOM_FIELD_VALUES``

**Type**: ``list``

**Default**: ``{}`` (empty dictionary)

**Description**: Defines custom values for specific fields in particular models during the data generation process. This setting allows users to specify exact values for certain fields instead of random or default-generated data, giving finer control over the generated dataset.

The dictionary's format follows `{ "app_label.ModelName": { "field_name": "custom_value" } }`.

For example:
```python
DATA_GENERATOR_CUSTOM_FIELD_VALUES = {
    "auth.User": {
        "first_name": "somebody",
        "email": "user@example.com",
    },
    "myapp.Product": {
        "price": 9.99,
        "stock": 100,
    },
}
```

In this example:

- The `auth.User` model's `first_name` field will always be set to `"somebody"`.

- The `myapp.Product` model's `price` and `stock` fields will always have values of `9.99` and `100`, respectively.

This setting is useful when certain fields require specific values, such as default usernames or predefined product prices, while other fields can still be generated with random or unique values.

---


### Final Notes:
- **Version Compatibility**: Ensure your project meets the compatibility requirements for both Django and Python versions.
- **Contributions**: Contributions are welcome! Feel free to check out the [Contributing guide](CONTRIBUTING.md) for more details.

If you encounter any issues or have feedback, please reach out via our [GitHub Issues page](https://github.com/lazarus-org/dj-data-generator/issues).
