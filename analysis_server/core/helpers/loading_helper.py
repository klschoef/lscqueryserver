import importlib

import os

def to_camel_case(snake_str):
    """Convert snake_case string to CamelCase string."""
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

def to_snake_case(camel_str):
    """Convert CamelCase string to snake_case string."""
    snake_str = ''
    for char in camel_str:
        if char.isupper():
            snake_str += '_' + char.lower()
        else:
            snake_str += char
    return snake_str.lstrip('_')

def discover_pipeline_classes(directory):
    """Discover and return all pipeline class names in a given directory."""
    class_names = []
    # List all python files in the specified directory
    for file in os.listdir(directory):
        if file.endswith("_pipeline.py"):
            # Remove '_pipeline.py' and convert to CamelCase
            base_name = file[:-3]  # remove the suffix
            class_name = to_camel_case(base_name)
            class_names.append(class_name)
    return class_names

def parse_pipelines_from_string(comma_separated_string):
    class_names = comma_separated_string.split(',')
    pipelines = []
    for class_name in class_names:
        # Convert CamelCase class name back to snake_case for module name
        module_snake_name = to_snake_case(class_name)
        module_name = f'core.processing_pipelines.{module_snake_name}'
        class_module = importlib.import_module(module_name)
        class_obj = getattr(class_module, class_name)
        pipelines.append(class_obj())
    return pipelines