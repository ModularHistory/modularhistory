import { AUTH_REDIRECT_PATH, handleLogin, handleLogout, LOGIN_PAGE_PATH } from "@/auth";
import SearchIcon from "@mui/icons-material/Search";
import { Box, Divider, InputAdornment, styled, TextField } from "@mui/material";
import { useSession } from "next-auth/client";
import Link from "next/link";
import { useRouter } from "next/router";
import { ParsedUrlQueryInput } from "querystring";
import React, {
  FC,
  KeyboardEventHandler,
  MouseEventHandler,
  MutableRefObject,
  useContext,
  useRef,
} from "react";
import Image from "react-bootstrap/Image";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import NavDropdown from "react-bootstrap/NavDropdown";
import PageTransitionContext from "./PageTransitionContext";

const fields = ["query"] as const;
type Field = typeof fields[number];
type FieldsRef = MutableRefObject<Record<Field, any>>;
type FieldCallbacks = Record<Field, (value: ParsedUrlQueryInput[string]) => void>;

const StyledTextField = styled(TextField)({
  backgroundColor: "white",
  minWidth: "20rem",
  maxWidth: "20rem",

  "& .MuiOutlinedInput-root": {
    "& fieldset": {
      borderColor: "white",
      borderStyle: "none",
    },
    "& input": {
      backgroundColor: "white",
    },
    "&:hover fieldset": {
      borderColor: "white",
    },
    "&:focused fieldset": {
      borderColor: "white",
    },
    "& .Mui-focused fieldset": {
      borderColor: "white",
    },
  },
});

interface GlobalMenuItem {
  title: string;
  path: string;
  reactive?: boolean;
  submenuItems?: GlobalMenuItemWithoutSubmenuItems[];
}

type GlobalMenuItemWithoutSubmenuItems = Omit<GlobalMenuItem, "submenuItems">;

const globalMenuItems: GlobalMenuItem[] = [
  {
    title: "About",
    path: "/",
    submenuItems: [
      { title: "Introduction", path: "/about/introduction", reactive: true },
      { title: "Mission", path: "/about/mission", reactive: true },
      { title: "Manifesto", path: "/about/manifesto", reactive: true },
    ],
  },
  { title: "Occurrences", path: "/occurrences", reactive: true },
  { title: "Quotes", path: "/quotes", reactive: true },
  { title: "Topics", path: "/topics", reactive: true },
  {
    title: "Other",
    path: "/",
    submenuItems: [
      { title: "Propositions", path: "/propositions", reactive: true },
      { title: "Sources", path: "/sources", reactive: true },
      { title: "Entities", path: "/entities", reactive: true },
      { title: "Images", path: "/images", reactive: true },
    ],
  },
];

function hasSubmenuItems(
  menuItem: GlobalMenuItem
): menuItem is GlobalMenuItem & Required<Pick<GlobalMenuItem, "submenuItems">> {
  return menuItem.submenuItems !== undefined;
}

const WrappedNavLink: FC<GlobalMenuItemWithoutSubmenuItems> = ({
  title,
  path,
  reactive = true,
}: GlobalMenuItemWithoutSubmenuItems) => {
  const router = useRouter();
  const active = router.pathname === path;

  const navLink = (
    <Nav.Link href={path} className={active ? "active" : ""}>
      {title}
    </Nav.Link>
  );

  if (reactive) {
    return <Link href={path}>{navLink}</Link>;
  } else {
    return navLink;
  }
};

type WrappedNavDropdownProps = Required<Pick<GlobalMenuItem, "title" | "submenuItems">>;

const WrappedNavDropdown: FC<WrappedNavDropdownProps> = ({
  title,
  submenuItems,
}: WrappedNavDropdownProps) => {
  return (
    <NavDropdown renderMenuOnMount title={title} id={`${title}-dropdown`}>
      {submenuItems.map((item) => (
        <WrappedNavLink key={item.path} {...item} />
      ))}
    </NavDropdown>
  );
};

interface GlobalNavbarProps {
  menuItems?: GlobalMenuItem[];
}

const GlobalNavbar: FC<GlobalNavbarProps> = ({ menuItems }: GlobalNavbarProps) => {
  menuItems = menuItems || globalMenuItems;

  const router = useRouter();
  // TODO: Create session type and remove this cast to `any`.
  const [session, loading] = useSession();

  const login: MouseEventHandler = (e) => {
    e.preventDefault();
    handleLogin(router);
  };

  const logout: MouseEventHandler = (e) => {
    e.preventDefault();
    session && handleLogout(session);
  };

  const fieldsRef = useRef(
    Object.fromEntries(fields.map((name) => [name, router.query[name]]))
  ) as FieldsRef;
  const fieldCallbacks = Object.fromEntries(
    fields.map((name) => [name, (value: any) => (fieldsRef.current[name] = value)])
  ) as FieldCallbacks;
  const isLoading = useContext(PageTransitionContext);

  const submitForm = () => {
    const queryParams = { ...fieldsRef.current };
    for (const name in queryParams) {
      if (!queryParams[name as Field]) delete queryParams[name as Field];
    }

    router.push({
      pathname: "/search",
      query: queryParams,
    });
  };

  const handleKeyUp: KeyboardEventHandler = (event) => {
    if (event.key === "Enter") {
      submitForm();
    }
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
          alt={session.user.name || session.user.handle}
          width="35"
          height="35"
        />
      );
    }
    accountControls = (
      <NavDropdown id="accountDropdown" title={accountDropdownIcon} renderMenuOnMount alignRight>
        <NavDropdown.Item href={`/users/${session.user.handle}`}>Profile</NavDropdown.Item>
        <NavDropdown.Item href={`/users/${session.user.handle}/settings`}>
          Settings
        </NavDropdown.Item>
        {(session.user.isSuperuser && (
          <>
            <Divider style={{ margin: "0.5rem 0" }} />
            <NavDropdown.Item href="/_admin/">Administrate</NavDropdown.Item>
            <Divider style={{ margin: "0.5rem 0" }} />
          </>
        )) || <Divider style={{ margin: "0.5rem 0" }} />}
        <NavDropdown.Item onClick={logout}>
          <span className="glyphicon glyphicon-log-out" /> Logout
        </NavDropdown.Item>
      </NavDropdown>
    );
  }

  return (
    <Navbar
      id="global-nav"
      bg="dark"
      variant="dark"
      style={{ minHeight: "4rem" }}
      expand="md"
      collapseOnSelect
      data-testid={"navbar"}
    >
      <Link href={"/"} passHref>
        <Navbar.Brand href={"/"} data-cy={"brand"}>
          <Image alt="Logo" src="/static/logo_head_white.png" width="50px" height="45px" />{" "}
          ModularHistory
        </Navbar.Brand>
      </Link>
      <Navbar.Toggle aria-controls="responsive-navbar-nav" />
      <Navbar.Collapse id="responsive-navbar-nav">
        <Nav className="mr-auto">
          {menuItems.map((item) =>
            hasSubmenuItems(item) ? (
              <WrappedNavDropdown key={item.title} {...item} />
            ) : (
              <WrappedNavLink key={item.title} {...item} />
            )
          )}
        </Nav>
        <Box
          sx={{
            paddingRight: "1.5rem",
            display: { xs: "none", sm: "none", md: "none", lg: "block" },
          }}
        >
          <StyledTextField
            defaultValue={fieldsRef.current.query}
            onChange={(e) => fieldCallbacks.query(e.target.value)}
            onKeyUp={handleKeyUp}
            disabled={isLoading}
            variant="outlined"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ fill: "gray" }} />
                </InputAdornment>
              ),
            }}
          />
        </Box>
        <Nav>{!hideAccountControls && !loading && accountControls}</Nav>
      </Navbar.Collapse>
    </Navbar>
  );
};

export default GlobalNavbar;
