import Container from "@material-ui/core/Container";
import { useSession } from 'next-auth/client';
import Head from 'next/head';
import { useRouter } from 'next/router';
import React from "react";
import Layout from "../../components/layout";


export default function Redirect(props) {
    const router = useRouter();
    const [session, loading] = useSession();
    const path = router.query.path ?? "/";
    const baseUrl = typeof window !== "undefined" ? window.location.origin : "";

    
    return (
        <>
            {session && !loading && (
                <Head>
                    <meta httpEquiv="refresh" content={`3; URL=${baseUrl}${path}`} />
                </Head>
            )}
            <Layout title={"Redirect"} canonicalUrl="/redirect">
                <Container>
                    <p className="lead text-center">Redirecting...</p>
                </Container>
            </Layout>
        </>
    );
}

// https://nextjs.org/docs/basic-features/data-fetching#getstaticprops-static-generation
export async function getStaticProps(context) {
  return {
    props: {}, // passed to the page component as props
  };
}
