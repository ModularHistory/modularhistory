import Layout from "@/components/Layout";
import { Box, Container, Typography } from "@mui/material";
import { GetServerSideProps } from "next";
import { getSession, useSession } from "next-auth/react";
import { NextSeo } from "next-seo";
import Head from "next/head";
import { useRouter } from "next/router";
import { setCookie } from "nookies";
import { FC, useEffect, useState } from "react";

interface RedirectProps {
  path?: string;
}

const Redirect: FC<RedirectProps> = ({ path }: RedirectProps) => {
  const router = useRouter();
  const { data: _session, status } = useSession();
  const loading = status === "loading";
  const [redirect, setRedirect] = useState(false);
  const baseUrl = typeof window !== "undefined" ? window.location.origin : "";
  const redirectPath = path ? `/${path}` : "";
  const redirectUrl = baseUrl + redirectPath;
  useEffect(() => {
    if (!loading) {
      // Choose redirect method based on whether the redirect URL
      // specifies a Django-served page or a Next.js-served page.
      if (/(\/_?admin\/?.*)/.test(redirectUrl)) {
        // If Django, redirect using meta tag.
        setRedirect(true);
      } else {
        // If Next.js, redirect using Next.js router.
        router.push(redirectPath);
      }
    }
  }, [loading, redirectPath, redirectUrl, router]);
  return (
    <>
      {!redirect && (
        <Head>
          <meta httpEquiv="refresh" content={`1; URL=${redirectUrl}`} />
        </Head>
      )}
      <Layout>
        <NextSeo title={"Redirect"} noindex />
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
  let { path } = context.params || {};
  if (Array.isArray(path)) {
    path = path.join("/");
  }

  const session = await getSession(context);
  if (typeof session?.sessionIdCookie == "string") {
    const [cookieName, cookieValue] = session.sessionIdCookie.split(";")[0].split("=");
    setCookie(context, cookieName, cookieValue, {
      secure: process.env.ENVIRONMENT === "prod",
      // expires: Date.parse(session.sessionIdCookie.match(/expires=(.+?);/)[1]);
      maxAge: parseInt(session.sessionIdCookie.match(/Max-Age=(.+?);/)?.[1] || "0"),
      sameSite: "lax",
      httpOnly: true,
      path: "/",
    });
  }
  return {
    props: { path: path ?? null }, // passed to the page component as props
  };
};
