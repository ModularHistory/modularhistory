# http://docs.pyinvoke.org/en/0.12.1/concepts/namespaces.html
import os

from invoke import Collection

from modularhistory.environment import IS_DEV

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modularhistory.settings')

from . import db, media, scm, setup, tasks  # noqa: E402

# http://docs.pyinvoke.org/en/latest/api/collection.html#invoke.collection.Collection.from_module
namespace = Collection.from_module(tasks)

if IS_DEV:
    from . import qa

    namespace.add_collection(qa)
    namespace.add_task(qa.lint)
    namespace.add_task(qa.test)

namespace.add_collection(db)
namespace.add_collection(media)

namespace.add_collection(scm)
namespace.add_task(scm.commit)

namespace.add_collection(setup)
namespace.add_task(setup.seed)
