# Inside your src/data/__init__.py
import pkgutil
import importlib

# Iterate through all the modules in the current package
for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
    # Import the module and assign it to a local variable based on its name
    module = importlib.import_module(f".{module_name}", __name__)
    # Add the module to the package's namespace
    globals()[module_name] = module