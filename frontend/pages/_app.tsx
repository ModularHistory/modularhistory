import "@/../core/static/styles/base.scss";
import { DJANGO_CSRF_COOKIE_NAME } from "@/auth";
import axiosWithoutAuth from "@/axiosWithoutAuth";
import { PageTransitionContextProvider } from "@/components/PageTransitionContext";
import { initializeSentry } from "@/sentry";
import "@/styles/globals.css";
import createCache from "@emotion/cache";
import { CacheProvider, EmotionCache } from "@emotion/react";
import { Box, Fade, LinearProgress } from "@material-ui/core";
import { createTheme, ThemeProvider } from "@material-ui/core/styles";
import { NextPage } from "next";
import { Provider, signOut, useSession } from "next-auth/client";
import { AppProps } from "next/app";
import Head from "next/head";
import { useRouter } from "next/router";
import { FC, ReactElement, useEffect, useRef, useState } from "react";
import Cookies from "universal-cookie";

initializeSentry();

const cookies = new Cookies();

const theme = createTheme({});

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
        <meta property="og:type" content="website" />
        {/* TODO: Use a better image. (This is the image that appears
                  in messaging apps when a link to the website is shared.) */}
        {/*<meta property="og:image" content="{% static 'logo_head_white.png' %}" />*/}
        <meta property="og:url" content="https://www.modularhistory.com/" />
        <meta property="og:title" content="ModularHistory" />
        <meta property="og:description" content="History, modularized." />
        <meta name="facebook-domain-verification" content="dfnrpkj6k5hhiqtxmtxsgw23xr8bfr" />
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
        <SessionKiller>
          <PageTransitionContextProvider>
            <ThemeProvider theme={theme}>
              <PageTransitionProgressBar />
              <Component {...pageProps} err={err} />
            </ThemeProvider>
          </PageTransitionContextProvider>
        </SessionKiller>
      </Provider>
    </CacheProvider>
  );
};

export default App;

const PageTransitionProgressBar: FC = () => {
  const { events } = useRouter();
  const [loadingProgress, setLoadingProgress] = useState(0);

  // We use this ref to track the last active interval/timeout
  // so we can cancel it when a transition is interrupted.
  const timerIDRef = useRef<number>();

  useEffect(() => {
    const clearProgressInterval = () => {
      if (timerIDRef.current) clearInterval(timerIDRef.current);
    };

    const handleRouteChangeStart = () => {
      clearProgressInterval();
      setLoadingProgress(20);

      // every 500ms, increase progress by 5, until we reach 80.
      timerIDRef.current = window.setInterval(() => {
        setLoadingProgress((currentProgress) => {
          if (currentProgress === 75) {
            clearProgressInterval();
          }
          return currentProgress + 5;
        });
      }, 500);
    };

    const handleRouteChangeComplete = () => {
      clearProgressInterval();
      setLoadingProgress(100);
      timerIDRef.current = window.setTimeout(() => setLoadingProgress(0), 1e3);
    };

    events.on("routeChangeStart", handleRouteChangeStart);
    events.on("routeChangeComplete", handleRouteChangeComplete);

    return () => {
      events.off("routeChangeStart", handleRouteChangeStart);
      events.off("routeChangeComplete", handleRouteChangeComplete);
    };
  }, [events]);

  return (
    <Box position={"fixed"} width={"100%"} top={-1} left={0} zIndex={10}>
      <Fade in={![0, 100].includes(loadingProgress)} timeout={{ exit: 1e3 }}>
        <LinearProgress
          variant={"determinate"}
          value={loadingProgress}
          key={Number(loadingProgress === 0)}
        />
      </Fade>
    </Box>
  );
};
