import { AUTH_COOKIES } from "@/auth";
import { useSession } from "next-auth/react";
import { FunctionComponent, useEffect } from "react";
import Footer from "./Footer";
import Navbar from "./Navbar";

const Layout: FunctionComponent = ({ children }) => {
  const { data: session } = useSession();

  // https://next-auth.js.org/tutorials/refresh-token-rotation#client-side
  useEffect(() => {
    // Set client-side cookies associated with the Django session.
    if (session) {
      if (Array.isArray(session.clientSideCookies)) {
        session.clientSideCookies.forEach((cookie) => {
          document.cookie = cookie;
          const debugMessage =
            process.env.ENVIRONMENT === "dev"
              ? `Updated ${cookie.split(";")[0].split("=")[0]} cookie to ${
                  cookie.split(";")[0].split("=")[1]
                }.`
              : `Updated ${cookie.split(";")[0].split("=")[0]} cookie.`;
          // eslint-disable-next-line no-console
          console.debug(debugMessage);
        });
      }
    } else {
      deleteAuthCookies();
    }
  }, [session]);

  return (
    <>
      <Navbar />
      <div className="main-content">{children}</div>
      <Footer />
      {/* Removed scripts template tag.
          Can be added to Head with defer attribute */}
    </>
  );
};

export default Layout;

const deleteAuthCookies = (): void => {
  AUTH_COOKIES.forEach((cookieName) => {
    document.cookie = `${cookieName}; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
  });
};
