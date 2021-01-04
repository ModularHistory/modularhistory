import Head from 'next/head'
import Navbar from './navbar'
import Footer from './footer'
import Modal from './modal'
import {useRouter} from "next/router";


export default function Layout({title, canonical_url, children}) {
  const router = useRouter();

  return (
    <>
      <Head>
        <title>{title || "Home"} | ModularHistory</title>
        <link rel="canonical" href={canonical_url || router.pathname} />
      </Head>
      <Navbar />

      <div className="main-content">
        {children}
      </div>

      <Footer />
      <Modal />
      {/* Removed scripts template tag.
          Can be added to Head with defer attribute */}
    </>
  )
}