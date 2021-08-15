// https://nextjs.org/docs/advanced-features/custom-document

import { ServerStyleSheets } from "@material-ui/styles";
import BaseDocument, { Head, Html, Main, NextScript } from "next/document";
import React from "react";

class Document extends BaseDocument {
  static async getInitialProps(ctx) {
    // Copied from https://github.com/mui-org/material-ui/blob/master/examples/nextjs/
    // Synchronizes server & client CSS for initial SSR

    // Render app and page and get the context of the page with collected side effects.
    const sheets = new ServerStyleSheets();
    const originalRenderPage = ctx.renderPage;

    ctx.renderPage = () =>
      originalRenderPage({
        enhanceApp: (App) => (props) => sheets.collect(<App {...props} />),
      });

    const initialProps = await BaseDocument.getInitialProps(ctx);

    return {
      ...initialProps,
      // Styles fragment is rendered after the app and page rendering finish.
      styles: [...React.Children.toArray(initialProps.styles), sheets.getStyleElement()],
    };
  }

  render() {
    return (
      <Html lang="en">
        <Head>
          {/* Google Tag Manager */}
          {/* TODO: https://www.npmjs.com/package/react-gtm-module */}
          {/*<script>*/}
          {/*    {(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':*/}
          {/*            new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],*/}
          {/*            j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=*/}
          {/*            'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);*/}
          {/*    })(window,document,'script','dataLayer','GTM-P68V7DK')}*/}
          {/*</script>*/}
          {/* End Google Tag Manager */}

          {/*<link rel="icon" href="{% static 'favicon.ico' %}" type="image/x-icon" />*/}

          {/* Font Awesome */}
          <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.11.2/css/all.css" />
          {/* Latest compiled and minified Bootstrap CSS */}
          <link
            rel="stylesheet"
            href="https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
          />

          {/* jQuery library */}
          {/* <Script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js" /> */}
          {/* Popper JS */}
          {/* <Script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js" /> */}
          {/* Latest compiled Bootstrap JavaScript */}
          {/* <Script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" /> */}
        </Head>
        <body>
          <Main />
          <NextScript />
        </body>
      </Html>
    );
  }
}

export default Document;
