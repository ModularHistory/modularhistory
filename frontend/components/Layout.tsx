import { AUTH_COOKIES } from "@/auth";
import { Box, Fade, LinearProgress } from "@material-ui/core";
import { useSession } from "next-auth/client";
import Head from "next/head";
import { useRouter } from "next/router";
import { FunctionComponent, PropsWithChildren, useEffect, useState } from "react";
import Footer from "./Footer";
import Navbar from "./Navbar";

interface LayoutProperties {
  title: string;
  canonicalUrl?: string;
}

const Layout: FunctionComponent<LayoutProperties> = ({
  title,
  canonicalUrl,
  children,
}: PropsWithChildren<LayoutProperties>) => {
  const router = useRouter();
  const [session, _loading] = useSession();
  const [loadingProgress, setLoadingProgress] = useState(1);

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

  useEffect(() => {
    const handleRouteChangeStart = () => {
      setLoadingProgress(20);
      const updateProgress = () =>
        setTimeout(() => {
          console.log("updating progress");
          setLoadingProgress((currentLoadingProgress) => {
            if (![0, 75, 100].includes(currentLoadingProgress)) {
              updateProgress();
            }
            return currentLoadingProgress + 5;
          });
        }, 500);
      updateProgress();
    };

    const handleRouteChangeComplete = () => {
      setLoadingProgress(100);
      setTimeout(() => setLoadingProgress(0), 500);
    };

    router.events.on("routeChangeStart", handleRouteChangeStart);
    router.events.on("routeChangeComplete", handleRouteChangeComplete);

    // If the component is unmounted, unsubscribe
    // from the event with the `off` method:
    return () => {
      router.events.off("routeChangeStart", handleRouteChangeStart);
      router.events.off("routeChangeComplete", handleRouteChangeComplete);
    };
  }, [router]);

  return (
    <>
      <Head>
        <title>{title || "Home"} | ModularHistory</title>
        <link rel="canonical" href={canonicalUrl || router.pathname} />
      </Head>
      <Box
      // sx={{
      //   "& .MuiLinearProgress-bar": {
      //     position: "absolute"
      //   }
      // }}
      >
        <Fade in={loadingProgress !== 0}>
          <LinearProgress variant={"determinate"} value={loadingProgress} />
        </Fade>
      </Box>
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
