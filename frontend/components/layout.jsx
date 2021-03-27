import { useSession } from 'next-auth/client';
import Head from 'next/head';
// import Modal from "./modal";
import { useRouter } from 'next/router';
import PropTypes from 'prop-types';
import React, { useEffect } from 'react';
import Footer from './footer';
import Navbar from './navbar';


export default function Layout({ title, canonicalUrl, children }) {
  const router = useRouter();
  const [session] = useSession();

  // https://next-auth.js.org/tutorials/refresh-token-rotation#client-side
  useEffect(() => {
    // Set any cookies associated with the session.
    if (session) {
      if (session.cookies) {
        session.cookies.forEach((cookie) => {
          document.cookie = cookie;
        });
        console.log('Updated cookies.');
      }
    }
  }, [session]);

  return (
    <>
      <Head>
        <title>{title || 'Home'} | ModularHistory</title>
        <link rel="canonical" href={canonicalUrl || router.pathname} />
      </Head>

      <Navbar />

      <div className="main-content">{children}</div>

      <Footer />
      {/*<Modal />*/}
      {/* Removed scripts template tag.
          Can be added to Head with defer attribute */}
    </>
  );
}
// https://reactjs.org/docs/typechecking-with-proptypes.html
Layout.propTypes = {
  title: PropTypes.string.isRequired,
  canonicalUrl: PropTypes.string,
  children: PropTypes.node
};
