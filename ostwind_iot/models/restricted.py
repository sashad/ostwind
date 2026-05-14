import logging
import warnings

from RestrictedPython import compile_restricted
from RestrictedPython.Guards import full_write_guard, safe_builtins
from RestrictedPython.PrintCollector import PrintCollector


# Whitelist of allowed modules
class AllowedModules:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.DEFAULT_CONTEXT = {
                }
            cls._instance.ALLOWED_MODULES = [
                'math',
                'datetime',
                'json',
                # Add other allowed modules here
            ]
            cls._instance.DISALLOWED_ENV_ATTRS = [
                'cr',
                'registry',
                'uid',
                'sudo',
            ]
            cls._instance.DISALLOWED_MODEL_ATTRS = [
            ]
        return cls._instance


allowed_modules = AllowedModules()

_logger = logging.getLogger(__name__)


class RestrictedRecordset:
    def __init__(
            self,
            recordset,
            ):
        self._recordset = recordset

    @classmethod
    def create(cls, recordset):
        if isinstance(recordset, cls):
            return recordset
        return cls(recordset)

    def __repr__(self):
        # Get the model name and IDs from the original recordset
        model_name = self._recordset._name
        ids = [str(record.id) for record in self._recordset]
        ids_str = ','.join(ids)
        return f"Restricted({model_name}({ids_str}))"

    def __iter__(self):
        # Return an iterator over wrapped records
        for record in self._recordset:
            yield RestrictedRecordset(record)

    def __len__(self):
        return len(self._recordset)

    def __getitem__(self, index):
        # Return a wrapped record or recordset
        return RestrictedRecordset(self._recordset[index])

    def __getattr__(self, attr):
        original_attr = getattr(self._recordset, attr)

        if hasattr(original_attr, 'env'):
            return RestrictedRecordset(original_attr)

        if attr == 'env':
            raise AttributeError(f"Access to '{attr}' of a record"
                                 " is not allowed. Use a global 'env' value.")

        if callable(original_attr):
            def wrapped_method(*args, **kwargs):
                result = original_attr(*args, **kwargs)
                if hasattr(result, 'env'):
                    return RestrictedRecordset(result)
                return result
            return wrapped_method

        return original_attr


class RestrictedModel:
    def __init__(
            self,
            model,
            disallowed_attrs=allowed_modules.DISALLOWED_MODEL_ATTRS,
            ):
        self._model = model
        self._disallowed_attrs = disallowed_attrs

    def __getattr__(self, attr):
        disallow = any(attr.find(disallowed_attr) >= 0
                       for disallowed_attr in self._disallowed_attrs)
        if attr[0] == '_' or disallow:
            raise AttributeError(f"Access to '{attr}' of '{self._model._name}'"
                                 f" model is not allowed.")
        # Allow access to other attributes
        return getattr(self._model, attr)

    def wrap_records(self, records):
        # Wrap a single model record in the RestrictedRecord proxy
        return RestrictedRecordset(records)

    def search(self, domain, *args, **kwargs):
        records = self._model.search(domain, *args, **kwargs)
        return self.wrap_records(records)

    def browse(self, ids, *args, **kwargs):
        records = self._model.browse(ids, *args, **kwargs)
        return self.wrap_records(records)


class RestrictedEnv:
    def __init__(self, env):
        self._env = env
        self._disallowed_attrs = allowed_modules.DISALLOWED_ENV_ATTRS

    @classmethod
    def create(cls, env):
        # Return the same object if it's already a RestrictedRecordset
        if isinstance(env, cls):
            return env
        return cls(env)

    def __repr__(self):
        return f"<RestrictedEnv object at {hex(id(self))}>"

    def __getitem__(self, model_name):
        return RestrictedModel(self._env[model_name], self._disallowed_attrs)

    def __getattr__(self, attr):
        # Explicitly block access to 'cr' and other sensitive attributes
        if attr in self._disallowed_attrs:
            raise AttributeError(f"Access to '{attr}' is not allowed.")
        # Allow access to other attributes
        return getattr(self._env, attr)


def safe_eval(code, records, env,
              allowed_modules,
              with_user_id,
              **params):

    def make_restricted_import(allowed_modules):
        def restricted_import(name, globals=None, locals=None, fromlist=(),
                              level=0):
            if name not in allowed_modules:
                raise ImportError(f"Import of module '{name}' is not allowed.")
            return __import__(name, globals, locals, fromlist, level)
        return restricted_import

    rec = None
    if records:
        rec = records.with_user(with_user_id)
        env = rec.env

    # Create a restricted import function with the allowed modules
    restricted_import = make_restricted_import(allowed_modules)

    printed = []
    captured_warnings = []

    # _logger.info(f"{dir(env['res.partner'])=}")
    # _logger.info(f"{dir(env['res.partner'].browse(1))=}")

    class CustomPrintCollector(PrintCollector):
        def write(self, text):
            # Append each print output to your external list
            printed.append(text)
            super().write(text)

    # Define _getitem_ to allow dictionary and list indexing
    def _getitem_(container, key):
        return container[key]

    restricted_globals = {
        '__builtins__': {
            **safe_builtins,
            '__import__': restricted_import,  # Custom import guard
        },
        '_getattr_': getattr,
        '_getiter_': iter,
        '_print_': CustomPrintCollector,
        '_write_': full_write_guard,
        '_getitem_': _getitem_,
        'env': RestrictedEnv(env),
        'context': env.context,
    }
    restricted_globals.update(params)
    if rec:
        restricted_globals['recordset'] = RestrictedRecordset(rec)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")  # Capture all warnings
        try:
            bytecode = compile_restricted(code, '<string>', 'exec')
            exec(bytecode, restricted_globals, {})
        except Exception as e:
            # raise Exception(f"Run script error: {e}")
            _logger.error(f"Run script error: {e}")
            return (f"Run script error: {e}", restricted_globals["context"],
                    None)

        captured_warnings.extend(w)
        warning_list = [str(warning.message) for warning in captured_warnings]

    return (printed, restricted_globals["context"], warning_list)


def set_default_context(context: dict = None):
    if context is None:
        context = {}
    if dict:
        AllowedModules().DEFAULT_CONTEXT = context


# def set_default_allowed_models(models: list = None):
#     if models:
#         AllowedModules().ALLOWED_MODELS = models


def set_default_allowed_modules(modules: list = None):
    if modules:
        AllowedModules().ALLOWED_MODULES = modules
