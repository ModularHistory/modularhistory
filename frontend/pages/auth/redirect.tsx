import Container from "@material-ui/core/Container";
import { useSession } from "next-auth/client";
import Head from "next/head";
import { useRouter } from "next/router";
import React from "react";
import Layout from "../../components/layout";

const Redirect: React.FunctionComponent = () => {
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
          <p className="lead text-center">Redirecting...</p>
        </Container>
      </Layout>
    </>
  );
};

export default Redirect;
