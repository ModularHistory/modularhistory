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
          {/* Material Design Bootstrap CSS */}
          <link
            rel="stylesheet"
            href="https://cdnjs.cloudflare.com/ajax/libs/mdbootstrap/4.4.1/css/mdb.min.css"
          />

          {/*Inheriting templates can add <link rel="stylesheet"> and/or <style> elements with the styles block.*/}
          {/*{% block styles %}{% endblock %}*/}

          {/* jQuery library */}
          <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js" />
          {/* Popper JS */}
          <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js" />
          {/* Latest compiled Bootstrap JavaScript */}
          <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" />

          {/* PDF.js */}
          {/* TODO: replace with node package and import where used
                    https://www.npmjs.com/package/pdfjs-dist */}
          <script src="https://cdn.jsdelivr.net/npm/pdfjs-dist@2/build/pdf.min.js" defer />
          {/* Epub.js */}
          {/* TODO: likewise, https://www.npmjs.com/package/epubjs */}
          <script src="https://cdn.jsdelivr.net/npm/epubjs/dist/epub.min.js" defer />

          {/*{% if request.user.is_superuser %}*/}
          {/*    <style>*/}
          {/*        .edit-object-button {display: inline;}*/}
          {/*    </style>*/}
          {/*{% endif %}*/}
          {/*<script type="text/javascript" src='{% static "scripts/base.js" %}' defer></script>*/}
          <style>
            {"#__next {display: flex; flex-direction: column; min-height: 100%}"}
          </style>
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
