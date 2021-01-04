import Head from 'next/head';
import {useRouter} from "next/router";


// redirect to Django if Next does not have a page
export default function Custom404({hostname}) {
  const router = useRouter();
  return (
    <Head>
      <title>404</title>
      <meta httpEquiv="refresh" content={`0; URL=${hostname}${router.asPath}`} />
    </Head>
  );
}

export async function getStaticProps() {
  return {
    props: {
      hostname: process.env.HOSTNAME,
    },
  };
}
