import { Box, Container, Typography } from "@material-ui/core";
import { GetServerSideProps } from "next";
import { getSession, useSession } from "next-auth/client";
import Head from "next/head";
import { useRouter } from "next/router";
import { setCookie } from "nookies";
import { FC } from "react";
import Layout from "../../components/Layout";

const Redirect: FC = () => {
  const router = useRouter();
  const [_session, loading] = useSession();
  const path = router.query.path ?? "/";
  const baseUrl = typeof window !== "undefined" ? window.location.origin : "";
  return (
    <>
      {!loading && (
        <Head>
          <meta httpEquiv="refresh" content={`1; URL=${baseUrl}${path}`} />
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
    props: {}, // passed to the page component as props
  };
};
