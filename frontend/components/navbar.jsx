import Link from 'next/link';
import { useRouter } from 'next/router';
import React from 'react';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';

// import Typography from '@material-ui/core/Typography';

// TODO: use App Bar component: https://material-ui.com/components/app-bar/

const logoImageSrc = '/static/logo_head_white.png';

const globalMenuItems = [
  {
    title: "About", children: [
      { title: "About Us", path: '/about', reactive: false },
      { title: "Manifesto", path: '/manifesto', reactive: false }
    ]
  },
  { title: "Occurrences", path: '/occurrences', reactive: false },
  { title: "Quotes", path: '/quotes', reactive: false },
  { title: "Entities", path: '/entities', reactive: true },
];

function WrappedNavLink({ title, path, reactive, ...childProps }) {
  const router = useRouter();
  const active = router.pathname === path;
  if (reactive) {
    return (
      <Link href={path}>
        <Nav.Link className={active ? "active" : ""}>{title}</Nav.Link>
      </Link>
    );
  } else {
    return (
      <Nav.Link href={path} className={active ? "active" : ""}>{title}</Nav.Link>
    );
  }
}

function WrappedNavDropdown({ title, children, ...childProps }) {
  return (
    <NavDropdown title={title} {...childProps} renderMenuOnMount>
      {children.map((item) => <NavDropdown.Item key={item.title} href={item.path}>{item.title}</NavDropdown.Item>)}
    </NavDropdown>
  )
}

export default function GlobalNavbar({ user, menuItems }) {
  user = user || { isAuthenticated: false };
  menuItems = menuItems || globalMenuItems;

  return (
    <Navbar id="global-nav" bg="dark" variant="dark" style={{ minHeight: "4rem" }} expand="md" collapseOnSelect>
      <Navbar.Brand href="/">
        <img
          alt="Logo"
          src={logoImageSrc}
          style={{ width: "2.7rem", height: "2.5rem" }}
        />{' '}
        ModularHistory
      </Navbar.Brand>
      <Navbar.Toggle aria-controls="responsive-navbar-nav" />
      <Navbar.Collapse id="responsive-navbar-nav">
        <Nav className="mr-auto">
          {menuItems.map((item) => (
            item.children ? <WrappedNavDropdown key={item.title} {...item} /> : <WrappedNavLink key={item.href} {...item} />
          ))}
        </Nav>
        <Nav>
          <NavDropdown id="accountDropdown" title={<i className="fas fa-user" />} renderMenuOnMount alignRight>
            <NavDropdown.Item href="/account/register">Create an account</NavDropdown.Item>
            <NavDropdown.Item href="/account/login">Log in</NavDropdown.Item>
          </NavDropdown>
        </Nav>
      </Navbar.Collapse>
    </Navbar>
  );
}
