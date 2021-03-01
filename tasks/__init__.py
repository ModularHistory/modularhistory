# http://docs.pyinvoke.org/en/0.12.1/concepts/namespaces.html
from invoke import Collection

from . import db, media, qa, scm, seeding, tasks

# http://docs.pyinvoke.org/en/latest/api/collection.html#invoke.collection.Collection.from_module
namespace = Collection.from_module(tasks)

namespace.add_collection(db)

namespace.add_collection(media)

namespace.add_collection(qa)
namespace.add_task(qa.lint)
namespace.add_task(qa.test)

namespace.add_collection(scm)
namespace.add_task(scm.commit)

namespace.add_collection(seeding)
namespace.add_task(seeding.seed)
