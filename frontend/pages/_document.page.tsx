// https://nextjs.org/docs/advanced-features/custom-document

import createCache from "@emotion/cache";
import createEmotionServer from "@emotion/server/create-instance";
import CssBaseline from "@mui/material/CssBaseline";
import BaseDocument, { DocumentContext, Head, Html, Main, NextScript } from "next/document";
import React from "react";

class Document extends BaseDocument {
  static async getInitialProps(ctx: DocumentContext) {
    // https://github.com/mui-org/material-ui/blob/7e7f40fff30ab0c2ec7a0003055a6508e11bcbb7/examples/nextjs/pages/_document.js
    // Synchronizes server & client CSS for initial SSR

    // Render app and page and get the context of the page with collected side effects.
    const originalRenderPage = ctx.renderPage;

    const cache = createCache({ key: "css" });
    const { extractCriticalToChunks } = createEmotionServer(cache);

    ctx.renderPage = () =>
      originalRenderPage({
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        // eslint-disable-next-line react/display-name
        enhanceApp: (App) => (props) => <App emotionCache={cache} {...props} />,
      });

    const initialProps = await BaseDocument.getInitialProps(ctx);

    // This is important. It prevents emotion from rendering invalid HTML.
    // See https://github.com/mui-org/material-ui/issues/26561#issuecomment-855286153
    const emotionStyles = extractCriticalToChunks(initialProps.html);
    const emotionStyleTags = emotionStyles.styles.map((style) => (
      <style
        data-emotion={`${style.key} ${style.ids.join(" ")}`}
        key={style.key}
        // eslint-disable-next-line react/no-danger
        dangerouslySetInnerHTML={{ __html: style.css }}
      />
    ));

    return {
      ...initialProps,
      // Styles fragment is rendered after the app and page rendering finish.
      styles: [...React.Children.toArray(initialProps.styles), ...emotionStyleTags],
    };
  }

  render() {
    return (
      <Html lang="en">
        <Head>
          <link rel="icon" href="/static/favicon.ico" type="image/x-icon" />

          <CssBaseline />

          {/* Font Awesome */}
          <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.11.2/css/all.css" />
          {/* Latest compiled and minified Bootstrap CSS */}
          <link
            rel="stylesheet"
            href="https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
          />
        </Head>
        <body>
          <Main />
          <NextScript />
          <div id="modal-root"></div>
        </body>
      </Html>
    );
  }
}

export default Document;
