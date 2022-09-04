# http://docs.pyinvoke.org/en/0.12.1/concepts/namespaces.html
import os

from invoke import Collection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from . import db, media, qa, search_utils, setup, tasks  # noqa: E402

# http://docs.pyinvoke.org/en/latest/api/collection.html#invoke.collection.Collection.from_module
namespace = Collection.from_module(tasks)

namespace.add_collection(qa)
namespace.add_task(qa.lint)
namespace.add_task(qa.test)

namespace.add_collection(db)
namespace.add_collection(media)

namespace.add_collection(setup)
namespace.add_task(setup.seed)

namespace.add_collection(search_utils)
namespace.add_task(search_utils.search)
