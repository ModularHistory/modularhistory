import axios from "axios";
import { Provider } from "next-auth/client";
import Head from "next/head";
import React, { useEffect } from "react";
import "../../modularhistory/static/styles/base.scss";

function MyApp({ Component, pageProps }) {
  useEffect(() => {
    // Get CSRF cookie
    const url = "/api/csrf/set";
    axios.get(url).then(console.log);
  }, []);
  return (
    <>
      <Head>
        {/*<title>Home | ModularHistory</title>*/}
        <meta charSet="UTF-8" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, shrink-to-fit=no"
        />
        <meta httpEquiv="Content-Language" content="en" />

        <meta property="og:type" content="website" />

        {/* TODO: Use a better image. (This is the image that appears
                  in messaging apps when a link to the website is shared.) */}
        {/*<meta property="og:image" content="{% static 'logo_head_white.png' %}" />*/}
        <meta property="og:url" content="https://www.modularhistory.com/" />
        <meta property="og:title" content="ModularHistory" />
        <meta property="og:description" content="History, modularized." />
      </Head>
      <noscript>
        <iframe
          src="https://www.googletagmanager.com/ns.html?id=GTM-P68V7DK"
          height="0"
          width="0"
          style={{ display: "none", visibility: "hidden" }}
        />
      </noscript>
      <Provider session={pageProps.session}>
        <Component {...pageProps} />
      </Provider>
    </>
  );
}

export default MyApp;
