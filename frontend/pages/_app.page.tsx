import "@/../../static/styles/base.scss";
import { DJANGO_CSRF_COOKIE_NAME } from "@/auth";
import axiosWithoutAuth from "@/axiosWithoutAuth";
import { PageTransitionContextProvider } from "@/components/PageTransitionContext";
import { initializeSentry } from "@/sentry";
import "@/styles/globals.css";
import createCache from "@emotion/cache";
import { CacheProvider, EmotionCache } from "@emotion/react";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import { NextPage } from "next";
import { SessionProvider, signOut, useSession } from "next-auth/react";
import { DefaultSeo } from "next-seo";
import { AppProps } from "next/app";
import dynamic from "next/dynamic";
import Head from "next/head";
import { FC, ReactElement, useEffect } from "react";
import SSRProvider from "react-bootstrap/SSRProvider";
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
  const { data: session } = useSession();
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
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <meta name="facebook-domain-verification" content="dfnrpkj6k5hhiqtxmtxsgw23xr8bfr" />
      </Head>
      <DefaultSeo
        description={"History, modularized."}
        openGraph={{
          type: "website",
          url: "https://modularhistory.orega.org/",
          site_name: "ModularHistory",
          // description: "History, modularized.",
          // images: [
          //   {
          //     url: 'https://www.example.ie/og-image.jpg',
          //     width: 800,
          //     height: 600,
          //     alt: 'Og Image Alt',
          //   },
          //   {
          //     url: 'https://www.example.ie/og-image-2.jpg',
          //     width: 800,
          //     height: 600,
          //     alt: 'Og Image Alt 2',
          //   },
          // ],
        }}
        twitter={{ handle: "@modularhistory" }}
        facebook={{
          appId: `${process.env.FACEBOOK_APP_ID}`,
        }}
        titleTemplate="%s | ModularHistory" // https://github.com/garmeeh/next-seo#title-template
        defaultTitle="ModularHistory" // https://github.com/garmeeh/next-seo#default-title
        additionalMetaTags={[
          {
            httpEquiv: "content-type",
            content: "text/html; charset=utf-8",
          },
          {
            name: "application-name",
            content: "ModularHistory",
          },
        ]}
        additionalLinkTags={
          [
            // {
            //   rel: 'icon',
            //   href: '/static/favicon.ico',
            // }
          ]
        }
      />
      <noscript>
        <iframe
          src="https://www.googletagmanager.com/ns.html?id=GTM-P68V7DK"
          height="0"
          width="0"
          style={{ display: "none", visibility: "hidden" }}
        />
      </noscript>
      <SessionProvider session={pageProps.session}>
        <SessionKiller>
          <PageTransitionContextProvider>
            <ThemeProvider theme={theme}>
              <SSRProvider>
                <DynamicPageTransitionProgressBar />
                <Component {...pageProps} err={err} />
              </SSRProvider>
            </ThemeProvider>
          </PageTransitionContextProvider>
        </SessionKiller>
      </SessionProvider>
    </CacheProvider>
  );
};

export default App;
