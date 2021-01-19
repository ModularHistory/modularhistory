import Head from "next/head";
// import Modal from "./modal";
// import { useRouter } from "next/router";
import React from 'react';
import Footer from "./footer";
import GlobalNavbar from "./navbar";


export default function Layout({title, children}) {
  // const router = useRouter();

  return (
    <>
      <Head>
        <title>{title || "Home"} | ModularHistory</title>
      </Head>

      <GlobalNavbar />

      <div className="main-content">
        {children}
      </div>

      <Footer />
      {/*<Modal />*/}
      {/* Removed scripts template tag.
          Can be added to Head with defer attribute */}
    </>
  );
}