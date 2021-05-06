import Layout from "@/components/Layout";
import { Box, Container, Typography } from "@material-ui/core";
import { GetServerSideProps } from "next";
import { getSession, useSession } from "next-auth/client";
import Head from "next/head";
import { useRouter } from "next/router";
import { setCookie } from "nookies";
import { FC, useEffect, useState } from "react";

interface RedirectProps {
  path: string;
}

const Redirect: FC<RedirectProps> = ({ path }: RedirectProps) => {
  const router = useRouter();
  const [_session, loading] = useSession();
  const [redirect, setRedirect] = useState(null);
  path = path ? `/${path}` : "";
  const baseUrl = typeof window !== "undefined" ? window.location.origin : "";
  const redirectUrl = `${baseUrl}${path}`;
  useEffect(() => {
    if (!loading) {
      // Choose redirect method based on whether the redirect URL
      // specifies a Django-served page or a Next.js-served page.
      if (/(\/admin\/?.*)/.test(redirectUrl)) {
        // If Django, redirect using meta tag.
        console.log(`>>>> Redirecting to ${redirectUrl} with meta`);
        setRedirect(true);
      } else {
        // If Next.js, redirect using Next.js router.
        console.log(`>>>> Redirecting to ${path} with Next.js`);
        router.push(path);
      }
    }
  }, [loading]);
  return (
    <>
      {!redirect && (
        <Head>
          <meta httpEquiv="refresh" content={`1; URL=${redirectUrl}`} />
        </Head>
      )}
      <Layout title={"Redirect"} canonicalUrl="/redirect">
        <Container>
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            m={5}
            p={5}
            flexDirection="column"
          >
            <Typography className="text-center">Redirecting...</Typography>
          </Box>
        </Container>
      </Layout>
    </>
  );
};

export default Redirect;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  let { path } = context.params;
  if (Array.isArray(path)) {
    path = path.join("/");
  } else if (!path) {
    path = null;
  }
  const session = await getSession(context);
  if (session) {
    const [cookieName, cookieValue] = session.sessionIdCookie.split(";")[0].split("=");
    setCookie(context, cookieName, cookieValue, {
      secure: process.env.ENVIRONMENT === "prod",
      // expires: Date.parse(session.sessionIdCookie.match(/expires=(.+?);/)[1]);
      maxAge: parseInt(session.sessionIdCookie.match(/Max-Age=(.+?);/)[1]),
      sameSite: "lax",
      httpOnly: true,
      path: "/",
    });
  }
  return {
    props: { path }, // passed to the page component as props
  };
};
