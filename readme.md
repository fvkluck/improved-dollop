# Readme

A small reproduction repo to point out a potential bug in the handling of natural keys in combination with multiple databases.

Ingredients
 1. 2 databases, 'default' and 'secondary'
 2. 2 models and a databaserouter
  * SomePrimaryModel lives in 'default'
  * SomeSecondaryModel lives in 'secondary'
 3. fixtures based on primary key
  * someprimarymodel.json
  * somesecondarymodel.json
 4. fixtures based on natural key
  * someprimarymodel_natural.json
  * somesecondarymodel_natural.json

The fixtures based on primary key can be loaded in both databases. If the model does not exist in the database, it is silently ignored and leads to a "installed 0 objects from 1 fixture" message.
When trying to load the fixtures based on natural key in the database in which the table does not exist, leads to an exception:

## Reproduction

1. python manage.py migrate
2. python manage.py migrate --database=secondary
3. python manage.py loaddata someprimarymodel_natural.json --database=secondary
4. python manage.py loaddata somesecondarymodel_natural.json


## Correct

Two commands that work correctly

> python manage.py loaddata someprimarymodel.json --database=secondary

> python manage.py loaddata somesecondarymodel.json

Both work great: installed 0 objects from 1 fixture


## Incorrect (Reproduction)

> python manage.py loaddata someprimarymodel_natural.json --database=secondary

> python manage.py loaddata somesecondarymodel_natural.json

Causes an exception to be raised. someprimarymodel.natural.json contains an instance of a model that does not exist in the secondary database.


## Context
----------

Data was created as follows:

> python manage.py shell

```
Python 3.11.4 (tags/v3.11.4:d2340ef, Jun  7 2023, 05:45:37) [MSC v.1934 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from myapp import models
>>> models.SomeSecondaryModel.objects.create(code="sec1")
<SomeSecondaryModel: SomeSecondaryModel object (1)>
>>> models.SomePrimaryModel.objects.create(code="prim1")
<SomePrimaryModel: SomePrimaryModel object (1)>
>>> exit()
```

Fixtures were created using:

> python manage.py dumpdata myapp.SomePrimaryModel -o someprimarymodel.json

> python manage.py dumpdata myapp.SomePrimaryModel --natural-primary -o someprimarymodel_natural.json

> python manage.py dumpdata myapp.SomeSecondaryModel -o somesecondarymodel.json --database=secondary

> python manage.py dumpdata myapp.SomeSecondaryModel --natural-primary -o somesecondarymodel_natural.json --database=secondary



## Full stacktrace

```
Traceback (most recent call last):
  File "some_folder\Lib\site-packages\django\db\backends\utils.py", line 89, in _execute
    return self.cursor.execute(sql, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "some_folder\Lib\site-packages\django\db\backends\sqlite3\base.py", line 328, in execute
    return super().execute(query, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sqlite3.OperationalError: no such table: myapp_somesecondarymodel

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "some_folder\Lib\site-packages\django\core\serializers\json.py", line 70, in Deserializer
    yield from PythonDeserializer(objects, **options)
  File "some_folder\Lib\site-packages\django\core\serializers\python.py", line 181, in Deserializer
    obj = base.build_instance(Model, data, using)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "some_folder\Lib\site-packages\django\core\serializers\base.py", line 344, in build_instance
    default_manager.db_manager(db).get_by_natural_key(*natural_key).pk
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "some_other_folder\natural-key-multi-db\repro\myapp\models.py", line 21, in get_by_natural_key
    return self.get(code=code)
           ^^^^^^^^^^^^^^^^^^^
  File "some_folder\Lib\site-packages\django\db\models\manager.py", line 87, in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "some_folder\Lib\site-packages\django\db\models\query.py", line 633, in get
    num = len(clone)
          ^^^^^^^^^^
  File "some_folder\Lib\site-packages\django\db\models\query.py", line 380, in __len__
    self._fetch_all()
  File "some_folder\Lib\site-packages\django\db\models\query.py", line 1881, in _fetch_all
    self._result_cache = list(self._iterable_class(self))
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "some_folder\Lib\site-packages\django\db\models\query.py", line 91, in __iter__
    results = compiler.execute_sql(
              ^^^^^^^^^^^^^^^^^^^^^
  File "some_folder\Lib\site-packages\django\db\models\sql\compiler.py", line 1562, in execute_sql
    cursor.execute(sql, params)
  File "some_folder\Lib\site-packages\django\db\backends\utils.py", line 102, in execute
    return super().execute(sql, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "some_folder\Lib\site-packages\django\db\backends\utils.py", line 67, in execute
    return self._execute_with_wrappers(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "some_folder\Lib\site-packages\django\db\backends\utils.py", line 80, in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "some_folder\Lib\site-packages\django\db\backends\utils.py", line 84, in _execute
    with self.db.wrap_database_errors:
  File "some_folder\Lib\site-packages\django\db\utils.py", line 91, in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
  File "some_folder\Lib\site-packages\django\db\backends\utils.py", line 89, in _execute
    return self.cursor.execute(sql, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "some_folder\Lib\site-packages\django\db\backends\sqlite3\base.py", line 328, in execute
    return super().execute(query, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
django.db.utils.OperationalError: no such table: myapp_somesecondarymodel

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "some_other_folder\natural-key-multi-db\repro\manage.py", line 22, in <module>
    main()
  File "some_other_folder\natural-key-multi-db\repro\manage.py", line 18, in main
    execute_from_command_line(sys.argv)
  File "some_folder\Lib\site-packages\django\core\management\__init__.py", line 442, in execute_from_command_line
    utility.execute()
  File "some_folder\Lib\site-packages\django\core\management\__init__.py", line 436, in execute
    self.fetch_command(subcommand).run_from_argv(self.argv)
  File "some_folder\Lib\site-packages\django\core\management\base.py", line 412, in run_from_argv
    self.execute(*args, **cmd_options)
  File "some_folder\Lib\site-packages\django\core\management\base.py", line 458, in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "some_folder\Lib\site-packages\django\core\management\commands\loaddata.py", line 102, in handle
    self.loaddata(fixture_labels)
  File "some_folder\Lib\site-packages\django\core\management\commands\loaddata.py", line 163, in loaddata
    self.load_label(fixture_label)
  File "some_folder\Lib\site-packages\django\core\management\commands\loaddata.py", line 251, in load_label
    for obj in objects:
  File "some_folder\Lib\site-packages\django\core\serializers\json.py", line 74, in Deserializer
    raise DeserializationError() from exc
django.core.serializers.base.DeserializationError: Problem installing fixture 'some_other_folder\natural-key-multi-db\repro\somesecondarymodel_natural.json':
```
