import { useSession } from "next-auth/client";
import Link from "next/link";
import { useRouter } from "next/router";
import PropTypes from "prop-types";
import React from "react";
import Image from "react-bootstrap/Image";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import NavDropdown from "react-bootstrap/NavDropdown";
import { AUTH_REDIRECT_PATH, handleLogin, handleLogout, LOGIN_PAGE_PATH } from "../auth";

const globalMenuItems = [
  {
    title: "About",
    path: "/about",
    children: [
      { title: "About Us", path: "/about", reactive: true },
      { title: "Manifesto", path: "/manifesto", reactive: true },
    ],
  },
  { title: "Occurrences", path: "/occurrences", reactive: true },
  { title: "Quotes", path: "/quotes", reactive: true },
  { title: "Topics", path: "/topics", reactive: true },
  {
    title: "Other",
    path: "/",
    children: [
      { title: "Propositions", path: "/propositions", reactive: true },
      { title: "Sources", path: "/sources", reactive: true },
      { title: "Entities", path: "/entities", reactive: true },
      { title: "Images", path: "/images", reactive: true },
    ],
  },
];

function WrappedNavLink({ title, path, as, reactive }) {
  const router = useRouter();
  const active = router.pathname === path;

  const navLink = (
    <Nav.Link href={path} className={active ? "active" : ""}>
      {title}
    </Nav.Link>
  );

  if (reactive) {
    return (
      <Link href={path} as={as}>
        {navLink}
      </Link>
    );
  } else {
    return navLink;
  }
}

function WrappedNavDropdown({ title, children, ...childProps }) {
  return (
    <NavDropdown renderMenuOnMount title={title} {...childProps}>
      {children.map((item) => (
        <WrappedNavLink key={item.path} {...item} />
      ))}
    </NavDropdown>
  );
}

// https://reactjs.org/docs/typechecking-with-proptypes.html
WrappedNavDropdown.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.arrayOf(PropTypes.object),
};

export default function GlobalNavbar({ menuItems }) {
  menuItems = menuItems || globalMenuItems;

  const router = useRouter();
  const [session, loading] = useSession();

  const login = (e) => {
    e.preventDefault();
    handleLogin(router);
  };

  const logout = (e) => {
    e.preventDefault();
    handleLogout(session);
  };

  const hideAccountControls =
    router.pathname === LOGIN_PAGE_PATH || router.pathname === AUTH_REDIRECT_PATH;
  let accountControls = (
    <Nav.Link onClick={login} href="/api/auth/signin">
      Sign in
    </Nav.Link>
  );
  let accountDropdownIcon = <i className="fas fa-user" />;

  if (session?.user) {
    if (session.user["avatar"]) {
      accountDropdownIcon = (
        <Image
          src={session.user.avatar}
          className="rounded-circle z-depth-0"
          alt={session.user.name}
          width="35"
          height="35"
        />
      );
    }
    if (session.user.isSuperuser) {
      accountControls = (
        <NavDropdown id="accountDropdown" title={accountDropdownIcon} renderMenuOnMount alignRight>
          <NavDropdown.Item href="/users/profile">Profile</NavDropdown.Item>
          {/* <NavDropdown.Item href="/users/setting">Settings</NavDropdown.Item> */}
          <NavDropdown.Item href="/_admin/">Administrate</NavDropdown.Item>
          {/* <NavDropdown.Item href="" className="hide-admin-controls">
            Hide admin controls
          </NavDropdown.Item> */}
          <NavDropdown.Item onClick={logout}>
            <span className="glyphicon glyphicon-log-out" /> Logout
          </NavDropdown.Item>
        </NavDropdown>
      );
    } else {
      accountControls = (
        <NavDropdown id="accountDropdown" title={accountDropdownIcon} renderMenuOnMount alignRight>
          <NavDropdown.Item onClick={logout}>
            <span className="glyphicon glyphicon-log-out" /> Logout
          </NavDropdown.Item>
        </NavDropdown>
      );
    }
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
      <Link href={"/"} passHref>
        <Navbar.Brand href={"/"} data-cy={"brand"}>
          <Image
            alt="Logo"
            src="/static/logo_head_white.png"
            width="50px"
            height="45px"
            layout="fixed"
          />{" "}
          ModularHistory
        </Navbar.Brand>
      </Link>
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
        <Nav>{!hideAccountControls && !loading && accountControls}</Nav>
      </Navbar.Collapse>
    </Navbar>
  );
}
// https://reactjs.org/docs/typechecking-with-proptypes.html
GlobalNavbar.propTypes = {
  menuItems: PropTypes.array,
};
