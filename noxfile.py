"""https://nox.thea.codes/en/stable/index.html."""

import nox
from nox.sessions import Session


@nox.session(python='3.7')
def lint(session: Session):
    """Install dependencies and run linters."""
    session.run('poetry', 'install')
    session.run('invoke', 'lint', '.')


@nox.session(python=['3.6', '3.7', '3.8'])
def test(session: Session):
    """Install dependencies and run tests."""
    session.run('poetry', 'install')
    session.run('invoke', 'test')
