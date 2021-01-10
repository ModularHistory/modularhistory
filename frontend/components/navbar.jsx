import Link from "next/link";

const globalMenuItems = [
  {title: "Occurrences", path: '/occurrences/', reactive: false},
  {title: "Quotes", path: '/quotes/', reactive: false},
  {title: "Entities", path: '/entities/', reactive: true},
  {title: "About", path: '/about/', reactive: false},
];

function MenuItem({title, path, reactive}) {
  return (
    <li className="nav-item">
      {reactive
        ? <Link href={path}>
          <a className="nav-link">{title}</a>
        </Link>
        : <a className="nav-link" href={path}>{title}</a>
      }
    </li>
  );
}

export default function Navbar({user, menuItems}) {
  user = user || {isAuthenticated: false};
  menuItems = menuItems || globalMenuItems;

  return (
    <nav className="navbar navbar-expand-sm bg-dark navbar-dark" id="global-nav" style={{minHeight: "4rem"}}>
      {/* Logo */}
      <a className="navbar-brand" href="/">
        <img src="/static/logo_head_white.png" alt="Logo" style={{height: "2.5rem"}}/>
        ModularHistory
      </a>

      {/* Non-collapsible links */}
      <div className="d-flex ml-auto order-1 order-sm-2">
        <ul className="navbar-nav">
          <li className="nav-item avatar dropdown">
            <a className="nav-link p-0 dropdown-toggle" id="accountDropdown" data-toggle="dropdown">
              <i className="fas fa-user"/>
              {/*{user.isAuthenticated && user.avatar*/}
              {/*  ? <img src={user.avatar.url}*/}
              {/*         className="rounded-circle z-depth-0"*/}
              {/*         alt={user.fullName} height="35"/>*/}
              {/*  : <i className="fas fa-user"/>*/}
              {/*}*/}
            </a>
            <div className="dropdown-menu dropdown-menu-right dropdown-default" aria-labelledby="accountDropdown">
              <a href="/account/register" className="dropdown-item">Create an account</a>
              <a href="/account/login" className="dropdown-item">Login</a>
              {/*{user.isAuthenticated*/}
              {/*  ? <>*/}
              {/*    <a className="dropdown-item" href="/account/profile">Profile</a>*/}
              {/*    <a className="dropdown-item" href="/account/setting">Settings</a>*/}
              {/*    {user.isSuperUser && <>*/}
              {/*      <a href="/admin/" className="dropdown-item">Administrate</a>*/}
              {/*      <a href="" className="dropdown-item hide-admin-controls">Hide admin controls</a>*/}
              {/*    </>}*/}
              {/*    <a href="/account/logout" className="dropdown-item">*/}
              {/*      <span className="glyphicon glyphicon-log-out"/> Logout*/}
              {/*    </a>*/}
              {/*  </>*/}
              {/*  : <>*/}
              {/*    <a href="/account/register" className="dropdown-item">Create an account</a>*/}
              {/*    <a href="/account/login" className="dropdown-item">Login</a>*/}
              {/*  </>*/}
              {/*}*/}
            </div>
          </li>
        </ul>
        {/* Toggler/collapser button */}
        <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#collapsibleNavbar">
          <span className="navbar-toggler-icon"/>
        </button>
      </div>

      {/* Collapsible links */}
      <div className="collapse navbar-collapse order-2 order-sm-1" id="collapsibleNavbar">
        <ul className="navbar-nav">
          {menuItems.map((item) => <MenuItem key={item.title} {...item}/>)}
        </ul>
        <ul className="navbar-nav ml-auto nav-flex-icons justify-content-end">
        </ul>
      </div>
    </nav>
  );
}