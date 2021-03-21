import { signIn, signOut, useSession } from "next-auth/client";
import Link from "next/link";
import { useRouter } from "next/router";
import PropTypes from 'prop-types';
import React from "react";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import NavDropdown from "react-bootstrap/NavDropdown";

// import Typography from '@material-ui/core/Typography';

// TODO: use App Bar component: https://material-ui.com/components/app-bar/

const logoImageSrc = "/static/logo_head_white.png";

const globalMenuItems = [
  {
    title: "About",
    path: "/about",
    children: [
      { title: "About Us", path: "/about", reactive: false },
      { title: "Manifesto", path: "/manifesto", reactive: false },
    ],
  },
  { title: "Occurrences", path: "/occurrences", reactive: false },
  { title: "Quotes", path: "/quotes", reactive: false },
  { title: "Entities", path: "/entities", reactive: true },
];

function WrappedNavLink({ title, path, reactive, ...childProps }) {
  const router = useRouter();
  const active = router.pathname === path;
  if (reactive) {
    return (
      <Link href={path}>
        <Nav.Link className={active ? "active" : ""} {...childProps}>
          {title}
        </Nav.Link>
      </Link>
    );
  } else {
    return (
      <Nav.Link href={path} className={active ? "active" : ""} {...childProps}>
        {title}
      </Nav.Link>
    );
  }
}

function WrappedNavDropdown({ title, children, ...childProps }) {
  return (
    <NavDropdown renderMenuOnMount title={title} {...childProps}>
      {children.map((item) => (
        <NavDropdown.Item key={item.path} href={item.path}>
          {item.title}
        </NavDropdown.Item>
      ))}
    </NavDropdown>
  );
}
// https://reactjs.org/docs/typechecking-with-proptypes.html
WrappedNavDropdown.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.arrayOf(PropTypes.object)
}

export default function GlobalNavbar({ menuItems }) {
  menuItems = menuItems || globalMenuItems;

  const [session] = useSession();

  const handleLogout = (e) => {
    e.preventDefault()
    signOut()
  }

  let accountDropdownIcon;
  if (session && session.user && session.user["avatar"]) {
    accountDropdownIcon = (
      <img
        src={session.user.avatar}
        className="rounded-circle z-depth-0"
        alt={session.user.name}
        height="35"
      />
    );
  } else {
    accountDropdownIcon = <i className="fas fa-user" />;
  }

  let accountControls;
  if (session && session.user) {
    if (session.user.is_superuser) {
      accountControls = (
        <>
          <NavDropdown.Item href="/account/profile">
            Profile
          </NavDropdown.Item>
          <NavDropdown.Item href="/account/setting">
            Settings
          </NavDropdown.Item>
          <NavDropdown.Item href="/admin/">
            Administrate
          </NavDropdown.Item>
          <NavDropdown.Item href="" className="hide-admin-controls">
            Hide admin controls
          </NavDropdown.Item>
          <NavDropdown.Item onClick={handleLogout}>
            <span className="glyphicon glyphicon-log-out" /> Logout
          </NavDropdown.Item>
        </>
      );
    } else {
      accountControls = (
        <>
          <NavDropdown.Item href="/account/profile">
            Profile
          </NavDropdown.Item>
          <NavDropdown.Item href="/account/settings">
            Settings
          </NavDropdown.Item>
          <NavDropdown.Item onClick={handleLogout}>
            <span className="glyphicon glyphicon-log-out" /> Logout
          </NavDropdown.Item>
        </>
      );
    }
  } else {
    accountControls = (
      <>
        <NavDropdown.Item href="/account/register">
          Create an account
        </NavDropdown.Item>
        <NavDropdown.Item onClick={signIn}>Log in</NavDropdown.Item>
      </>
    )
  }

  return (
    <Navbar
      id="global-nav"
      bg="dark"
      variant="dark"
      style={{ minHeight: "4rem" }}
      expand="md"
      collapseOnSelect
    >
      <Navbar.Brand href="/">
        <img
          alt="Logo"
          src={logoImageSrc}
          style={{ width: "2.7rem", height: "2.5rem" }}
        />{" "}
        ModularHistory
      </Navbar.Brand>
      <Navbar.Toggle aria-controls="responsive-navbar-nav" />
      <Navbar.Collapse id="responsive-navbar-nav">
        <Nav className="mr-auto">
          {menuItems.map((item) =>
            item.children ? (
              <WrappedNavDropdown key={item.title} {...item} />
            ) : (
              <WrappedNavLink key={item.title} {...item} />
            )
          )}
        </Nav>
        <Nav>
          <NavDropdown
            id="accountDropdown"
            title={accountDropdownIcon}
            renderMenuOnMount
            alignRight
          >
            { accountControls }
          </NavDropdown>
        </Nav>
      </Navbar.Collapse>
    </Navbar>
  );
}
// https://reactjs.org/docs/typechecking-with-proptypes.html
GlobalNavbar.propTypes = {
  menuItems: PropTypes.array,
}
