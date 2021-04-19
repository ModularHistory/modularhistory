import { Provider } from "next-auth/client";
import { AppProps } from "next/app";
import Head from "next/head";
import { useRouter } from "next/router";
import React, { useEffect } from "react";
import "../../core/static/styles/base.scss";
import { PageTransitionContextProvider } from "../components/PageTransitionContext";
import "../styles/globals.css";

const App = ({ Component, pageProps }: AppProps) => {
  const router = useRouter();
  useEffect(() => {
    // Remove the server-side injected CSS.
    // See https://github.com/mui-org/material-ui/blob/master/examples/nextjs/.
    const jssStyles = document.querySelector("#jss-server-side");
    if (jssStyles) {
      jssStyles.parentElement.removeChild(jssStyles);
    }
    // TODO: https://modularhistory.atlassian.net/browse/MH-148
    // Get Django CSRF cookie.
    // const url = "/api/csrf/set";
    // axios.get(url).then(console.log);

    // The next/Link component automatically handles page scrolling,
    // but router.push() does not. This event listener scrolls the page
    // any time router.push() is used.
    const handle = () => window.scrollTo({ top: 0, left: 0, behavior: "smooth" });
    router.events.on("routeChangeComplete", handle);
    return () => router.events.off("routerChangeComplete", handle);
  }, []);

  return (
    <>
      <Head>
        {/*<title>Home | ModularHistory</title>*/}
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
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
        <PageTransitionContextProvider>
          <Component {...pageProps} />
        </PageTransitionContextProvider>
      </Provider>
    </>
  );
};

export default App;
