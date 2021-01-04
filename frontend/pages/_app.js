import Head from 'next/head'
import '../../modularhistory/static/styles/base.scss'
import 'mdbreact/dist/css/mdb.css'

function MyApp({ Component, pageProps }) {
  return (
    <>
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
      </Head>
      <noscript>
        <iframe src="https://www.googletagmanager.com/ns.html?id=GTM-P68V7DK"
                height="0" width="0" style={{display: 'none', visibility: 'hidden'}} />
      </noscript>
      <Component {...pageProps} />
    </>
  );
}

export default MyApp
