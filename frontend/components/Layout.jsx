import { useSession } from "next-auth/client";
import Head from "next/head";
import { useRouter } from "next/router";
import PropTypes from "prop-types";
import React, { useEffect } from "react";
import { AUTH_COOKIES } from "../auth";
import Footer from "./Footer";
import Navbar from "./Navbar";

export default function Layout({ title, canonicalUrl, children }) {
  const router = useRouter();
  const [session, _loading] = useSession();

  // https://next-auth.js.org/tutorials/refresh-token-rotation#client-side
  useEffect(() => {
    // Set client-side cookies associated with the Django session.
    if (session) {
      if (session.clientSideCookies) {
        session.clientSideCookies.forEach((cookie) => {
          document.cookie = cookie;
          const cookieNameAndValue = cookie.split(";")[0].split("=");
          console.log(`Updated ${cookieNameAndValue[0]} cookie to ${cookieNameAndValue[1]}.`);
        });
      }
    } else {
      console.log("Not authenticated.");
      // Remove all auth cookies.
      AUTH_COOKIES.forEach((cookieName) => {
        document.cookie = `${cookieName}; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
      });
    }
  }, [session?.clientSideCookies]);

  return (
    <>
      <Head>
        <title>{title || "Home"} | ModularHistory</title>
        <link rel="canonical" href={canonicalUrl || router.pathname} />
      </Head>
      <Navbar />
      <div className="main-content">{children}</div>
      <Footer />
      {/* Removed scripts template tag.
          Can be added to Head with defer attribute */}
    </>
  );
}
// https://reactjs.org/docs/typechecking-with-proptypes.html
Layout.propTypes = {
  title: PropTypes.string.isRequired,
  canonicalUrl: PropTypes.string,
  children: PropTypes.node,
};
