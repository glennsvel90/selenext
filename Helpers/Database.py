import Middleware
import Models


class JambiBase(object):
    """ The base `Jambi` Object.  The actual `Jambi` class uses `JambiBase` as it's backbone. """

    def __init__(self):
        models_sub = [
            'BareField', 'BaseModel', 'BigIntegerField',
            'BinaryField', 'BlobField', 'BooleanField',
            'CharField', 'Check', 'Clause', 'CompositeKey',
            'DQ', 'DataError', 'DatabaseError', 'DateField',
            'DateTimeField', 'DecimalField', 'DeferredRelation',
            'DoesNotExist', 'DoubleField', 'Field', 'FixedCharField',
            'FloatField', 'ForeignKeyField', 'ImproperlyConfigured',
            'IntegerField', 'IntegrityError', 'InterfaceError',
            'InternalError', 'JOIN', 'JOIN_FULL', 'JOIN_INNER',
            'JOIN_LEFT_OUTER', 'Model', 'MySQLDatabase',
            'NotSupportedError', 'OperationalError', 'Param',
            'PostgresqlDatabase', 'PrimaryKeyField', 'ProgrammingError',
            'Proxy', 'R', 'SQL', 'SqliteDatabase', 'TextField',
            'TimeField', 'UUIDField', 'Using', 'Window',
            '__builtins__', '__doc__', '__file__', '__name__',
            '__package__', 'datetime', 'db', 'env', 'fn',
            'get_database', 'prefetch'
        ]

        # This next block starts importing Middleware for the models that exist.
        # Grab directory of Models.
        models = dir(Models)
        for model in models:
            # Check to see if we need to import Middleware.
            if model not in models_sub:
                middleware_name = model + 'Middleware'
                # Import the Middleware.
                exec ('from Middleware.{} import {}'.format(middleware_name, middleware_name))

        self.is_atomic = False

    def _get_modified_func_params(self, model, function, **kwargs):
        """ Run a peewee model function and modify the parameters. """

        # Get the Middleware's class name based on Model class name.
        class_name = model.__name__.strip()
        middleware_name = class_name + 'Middleware'
        if middleware_name in dir(Middleware):
            # Get the Middleware child classes file name based on middleware_name
            middleware_file_name = getattr(Middleware, middleware_name)
            # Get the Middleware child classes name based on the middleware_name and filename
            middleware_class = getattr(middleware_file_name, middleware_name)
            # Instantiate the child class.
            middleware_class_instance = middleware_class()
            modified_outputs = middleware_class_instance._modify_function_output(function, **kwargs)
            return modified_outputs
        return False

    def _get_modified_inputs(self, model, **kwargs):
        # Get the Middleware's class name based on Model class name.
        class_name = model.__name__.strip()
        middleware_name = class_name + 'Middleware'
        if middleware_name in dir(Middleware):
            # Get the Middleware child classes file name based on middleware_name
            middleware_file_name = getattr(Middleware, middleware_name)
            # Get the Middleware child classes name based on the middleware_name and filename
            middleware_class = getattr(middleware_file_name, middleware_name)
            # Instantiate the child class.
            middleware_class_instance = middleware_class()
            modified_inputs = middleware_class_instance._modify_in(**kwargs)
            return modified_inputs

        return False

    def _get_modified_query_outputs(self, model, query):
        # Get the Middleware's class name based on Model class name.
        class_name = model.__name__.strip()
        middleware_name = class_name + 'Middleware'
        if middleware_name in dir(Middleware):

            # Get the Middleware child classes file name based on middleware_name
            middleware_file_name = getattr(Middleware, middleware_name)
            # Get the Middleware child classes name based on the middleware_name and filename
            middleware_class = getattr(middleware_file_name, middleware_name)
            # Instantiate the child class.
            middleware_class_instance = middleware_class()
            modified_outputs = middleware_class_instance._modify_query_output(query)
            return modified_outputs
        return False

    def atomic(self, is_atomic=True):
        """ Enable peewee's atomic queries if the method supports it. """

        self.is_atomic = is_atomic
        return self

    def create(self, model, **kwargs):
        """ Run Middleware on peewee's `create` method. """

        # Modify kwargs
        kwargs = self._get_modified_inputs(model, **kwargs)
        # Get a model instance and save it peewee style.
        model_instance = model.create(**kwargs)
        return model_instance

    def grant_wish(self):
        """ Grand a wish. """

        from random import choice
        rand_starts = [
            "Mecca lecca hi, mecca hiney ho.",
            "Wish? Did somebody say 'Wish'?"
        ]
        rand_finishes = [
            "The wish has been granted. All hail Jambi!",
            "The wish has been granted. Long live Jambi!"
        ]
        print choice(rand_starts)
        print choice(rand_finishes)
        return self

    def insert(self, model, **kwargs):
        """ Run Middleware on peewee's `insert` method. """

        kwargs = self._get_modified_inputs(model, **kwargs)
        return model.insert(**kwargs).execute()

    def insert_many(self, model, data_source):
        """ Run Middleware on peewee's `insert_many` method. """

        for key, data_dict in enumerate(data_source):
            data_source[key] = self._get_modified_inputs(model, **data_dict)

        # print data_source
        if not self.is_atomic:
            return model.insert_many(data_source).execute()

        from Config.Environment import env, get_database
        db = get_database(env("DB_TYPE"))
        with db.atomic():
            return model.insert_many(data_source).execute()

    def model_func(self, function, **kwargs):
        """ Run a model function that takes **kwargs. """

        kwarg_keys = kwargs.keys()

        if 'model' in kwarg_keys:
            model = kwargs['model']
        else:
            model = function.im_self
        return self._get_modified_func_params(model, function, **kwargs)

    def model_func_pull(self, function, **kwargs):
        """ Run a model function but only modify outputs. """

        kwargs['mod_in'] = False
        return self.model_func(function, **kwargs)

    def model_func_push(self, function, **kwargs):
        """ Run a model function but only modify inputs. """
        kwargs['mod_out'] = False
        return self.model_func(function, **kwargs)

    def query(self, model, query):
        """ Run a query on a model. """

        # print dir(query)
        query_results = self._get_modified_query_outputs(model, query)
        return query_results


class Jambi(object):
    def __init__(self, model):
        if model.__class__.__name__ != 'BaseModel':
            raise TypeError('`model` must be a peewee model instance or a `BaseModel` instance.')

        self.jambi = JambiBase()
        self.model = model
        self.do_atomic = False

    def atomic(self, is_atomic=True):
        self.do_atomic = is_atomic
        return self

    def create(self, **kwargs):
        return self.jambi.create(self.model, **kwargs)

    def insert(self, **kwargs):
        return self.jambi.insert(self.model, **kwargs)

    def insert_many(self, data_source):
        j = self.jambi.atomic()
        if self.do_atomic:
            # Unset the flag.
            self.atomic(is_atomic=False)
            return j.insert_many(self.model, data_source)
        return self.jambi.insert_many(self.model, data_source)

    def model_func(self, function_name, **kwargs):
        function = getattr(self.model, function_name)
        return self.jambi.model_func(function, **kwargs)

    def model_func_pull(self, function_name, **kwargs):
        function = getattr(self.model, function_name)
        return self.jambi.model_func_pull(function, **kwargs)

    def model_func_push(self, function_name, **kwargs):
        function = getattr(self.model, function_name)
        return self.jambi.model_func_push(function, **kwargs)

    def query(self, query):
        return self.jambi.query(self.model, query)
