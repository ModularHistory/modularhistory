import ClickAwayListener from '@material-ui/core/ClickAwayListener';
import Grow from '@material-ui/core/Grow';
import MenuItem from '@material-ui/core/MenuItem';
import MenuList from '@material-ui/core/MenuList';
import Paper from '@material-ui/core/Paper';
import Popper from '@material-ui/core/Popper';
// import Typography from '@material-ui/core/Typography';
import Link from "next/link";
import React from 'react';

// TODO: use App Bar component: https://material-ui.com/components/app-bar/

const globalMenuItems = [
  {
    title: "About", children: [
      { title: "About Us", path: '/about/', reactive: false },
      { title: "Manifesto", path: '/manifesto/', reactive: false }
    ]
  },
  { title: "Occurrences", path: '/occurrences/', reactive: false },
  { title: "Quotes", path: '/quotes/', reactive: false },
  { title: "Entities", path: '/entities/', reactive: true },
];

function WrappedMenuItem({ title, path, reactive, ...childProps }) {
  return (
    <MenuItem {...childProps}>
      {reactive
        ?
        <Link href={path}>
          <a className="nav-link">{title}</a>
        </Link>
        :
        <a className="nav-link" href={path}>{title}</a>
      }
    </MenuItem>
  );
}

function MenuDropdown({ title, children }) {

  const [open, setOpen] = React.useState(false);
  const anchorRef = React.useRef(null);

  const handleToggle = () => {
    setOpen((prevOpen) => !prevOpen);
  };

  const handleClose = (event) => {
    if (anchorRef.current && anchorRef.current.contains(event.target)) {
      return;
    }

    setOpen(false);
  };

  function handleListKeyDown(event) {
    if (event.key === 'Tab') {
      event.preventDefault();
      setOpen(false);
    }
  }

  // return focus to the button when we transitioned from !open -> open
  const prevOpen = React.useRef(open);
  React.useEffect(() => {
    if (prevOpen.current === true && open === false) {
      anchorRef.current.focus();
    }

    prevOpen.current = open;
  }, [open]);

  return (
    <>
      <MenuItem
        ref={anchorRef}
        aria-controls={open ? 'menu-list-grow' : undefined}
        aria-haspopup="true"
        onClick={handleToggle}
      >
        <a className="nav-link">{title}</a>
      </MenuItem>
      <Popper open={open} anchorEl={anchorRef.current} role={undefined} transition disablePortal>
        {({ TransitionProps, placement }) => (
          <Grow
            {...TransitionProps}
            style={{ transformOrigin: placement === 'bottom' ? 'center top' : 'center bottom' }}
          >
            <Paper>
              <ClickAwayListener onClickAway={handleClose}>
                <MenuList autoFocusItem={open} id="menu-list-grow" onKeyDown={handleListKeyDown} className="bg-dark">
                  {children.map((item) => <WrappedMenuItem key={item.title} onClick={handleClose} {...item} />)}
                </MenuList>
              </ClickAwayListener>
            </Paper>
          </Grow>
        )}
      </Popper>
    </>
  );
}

export default function Navbar({ menuItems }) {
  menuItems = menuItems || globalMenuItems;

  const { user, isAuthenticated } = useAuth();

  return (
    <nav className="navbar navbar-expand-sm bg-dark navbar-dark" id="global-nav" style={{ minHeight: "4rem" }}>
      {/* Logo */}
      <a className="navbar-brand" href="/">
        <img src="/static/logo_head_white.png" alt="Logo" style={{ height: "2.5rem" }} />
        ModularHistory
      </a>

      {/* Non-collapsible links */}
      <div className="d-flex ml-auto order-1 order-sm-2">
        <ul className="navbar-nav">
          <li className="nav-item avatar dropdown">
            <a className="nav-link p-0 dropdown-toggle" id="accountDropdown" data-toggle="dropdown">
              {user && user['avatar']
                ? <img src={user.avatar}
                  className="rounded-circle z-depth-0"
                  alt={user.name} height="35" />
                : <i className="fas fa-user" />
              }
            </a>
            <div className="dropdown-menu dropdown-menu-right dropdown-default" aria-labelledby="accountDropdown">
              {user
                ? <>
                  <a className="dropdown-item" href="/account/profile">Profile</a>
                  <a className="dropdown-item" href="/account/setting">Settings</a>
                  {user.isSuperUser && <>
                    <a href="/admin/" className="dropdown-item">Administrate</a>
                    <a href="" className="dropdown-item hide-admin-controls">Hide admin controls</a>
                  </>}
                  <a href="/account/logout" className="dropdown-item">
                    <span className="glyphicon glyphicon-log-out" /> Logout
                  </a>
                </>
                : <>
                  <a href="/account/register" className="dropdown-item">Create an account</a>
                  <a href="/account/login" className="dropdown-item">Login</a>
                </>
              }
            </div>
          </li>
        </ul>
        {/* Toggler/collapser button */}
        <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#collapsibleNavbar">
          <span className="navbar-toggler-icon" />
        </button>
      </div>

      {/* Collapsible links */}
      <div className="collapse navbar-collapse order-2 order-sm-1" id="collapsibleNavbar">
        <ul className="navbar-nav">
          {menuItems.map((item) => (
            item.children ? <MenuDropdown key={item.title} {...item} /> : <WrappedMenuItem key={item.title} {...item} />
          ))}
        </ul>
        <ul className="navbar-nav ml-auto nav-flex-icons justify-content-end">
        </ul>
      </div>
    </nav>
  );
}
