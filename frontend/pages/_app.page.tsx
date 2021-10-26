import "@/../core/static/styles/base.scss";
import { DJANGO_CSRF_COOKIE_NAME } from "@/auth";
import axiosWithoutAuth from "@/axiosWithoutAuth";
import { PageTransitionContextProvider } from "@/components/PageTransitionContext";
import { initializeSentry } from "@/sentry";
import "@/styles/globals.css";
import createCache from "@emotion/cache";
import { CacheProvider, EmotionCache } from "@emotion/react";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { NextPage } from "next";
import { Provider, signOut, useSession } from "next-auth/client";
import { DefaultSeo } from "next-seo";
import { AppProps } from "next/app";
import dynamic from "next/dynamic";
import Head from "next/head";
import { FC, ReactElement, useEffect } from "react";
import TagManager from "react-gtm-module";
import Cookies from "universal-cookie";

initializeSentry();

const tagManagerArgs = {
  gtmId: "GTM-P68V7DK",
};

const DynamicPageTransitionProgressBar = dynamic(
  () => import("@/components/PageTransitionProgressBar")
);

export type GlobalTheme = typeof theme;

const theme = createTheme({});
const cookies = new Cookies();
const clientSideEmotionCache = createCache({ key: "css" });

interface SessionKillerProps {
  children: ReactElement;
}

const SessionKiller: FC<SessionKillerProps> = ({ children }: SessionKillerProps) => {
  const [session, _loading] = useSession();
  useEffect(() => {
    if (session?.expired) {
      signOut();
    }
  }, [session?.expired]);
  return children;
};

interface ExtendedAppProps extends AppProps {
  emotionCache: EmotionCache;
  err?: string;
}

const App: NextPage<ExtendedAppProps> = ({
  Component,
  pageProps,
  emotionCache = clientSideEmotionCache,
  err,
}: ExtendedAppProps) => {
  useEffect(() => {
    // Initialize Google Tag Manager.
    TagManager.initialize(tagManagerArgs);
    // Set the Django CSRF cookie if necessary.
    if (!cookies.get(DJANGO_CSRF_COOKIE_NAME)) {
      // Get Django CSRF cookie.
      // eslint-disable-next-line no-console
      const url = "/api/csrf/set/";
      axiosWithoutAuth.get(url);
    }
  }, []);

  return (
    <CacheProvider value={emotionCache}>
      <Head>
        {/*<title>Home | ModularHistory</title>*/}
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <meta httpEquiv="Content-Language" content="en" />
        <meta name="facebook-domain-verification" content="dfnrpkj6k5hhiqtxmtxsgw23xr8bfr" />
      </Head>
      <DefaultSeo
        openGraph={{
          type: "website",
          url: "https://www.modularhistory.com/",
          site_name: "ModularHistory",
          description: "History, modularized.",
        }}
        twitter={{ handle: "@modularhistory" }}
        titleTemplate="%s | ModularHistory" // https://github.com/garmeeh/next-seo#title-template
        defaultTitle="ModularHistory" // https://github.com/garmeeh/next-seo#default-title
      />
      <noscript>
        <iframe
          src="https://www.googletagmanager.com/ns.html?id=GTM-P68V7DK"
          height="0"
          width="0"
          style={{ display: "none", visibility: "hidden" }}
        />
      </noscript>
      <Provider session={pageProps.session}>
        <SessionKiller>
          <PageTransitionContextProvider>
            <ThemeProvider theme={theme}>
              <DynamicPageTransitionProgressBar />
              <Component {...pageProps} err={err} />
            </ThemeProvider>
          </PageTransitionContextProvider>
        </SessionKiller>
      </Provider>
    </CacheProvider>
  );
};

export default App;
