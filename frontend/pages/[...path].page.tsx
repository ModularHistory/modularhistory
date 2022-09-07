import Layout from "@/components/Layout";
import { FlatPage as FlatPageType } from "@/types/modules";
import { Container, useMediaQuery } from "@mui/material";
import axios from "axios";
import { GetStaticPaths, GetStaticProps } from "next";
import { NextSeo } from "next-seo";
import { FC } from "react";

export interface FlatPageProps {
  page: FlatPageType;
}

const FlatPage: FC<FlatPageProps> = ({ page }: FlatPageProps) => {
  // check if the viewport width is less than 36rem
  const isSmall = useMediaQuery("@media (max-width:36rem)");

  return (
    <Layout>
      <NextSeo title={page.title} canonical={page.path} description={page.metaDescription} />
      <Container style={{ padding: `1.25rem ${isSmall ? "1.25rem" : "5rem"}`, maxWidth: "50rem" }}>
        <h1>{page.title}</h1>
        <div dangerouslySetInnerHTML={{ __html: page.content }} />
      </Container>
    </Layout>
  );
};
export default FlatPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let page = null;
  let notFound = false;
  let { path } = params || {};
  if (Array.isArray(path)) {
    path = path.join("/");
  } else {
    path = path ?? "";
  }

  const getRedirectPath = async (path: string) => {
    let redirectPath = "";
    await axios
      .get(`http://${process.env.DJANGO_HOSTNAME}:${process.env.DJANGO_PORT}/api/redirects//${path}/`)
      .then((response) => {
        redirectPath = response.data.newPath;
      })
      .catch((error) => {
        if (error.response?.status === 404) {
          notFound = true;
        } else {
          throw error;
        }
      });
    return redirectPath;
  };

  const retrieveFlatPage = async (path: string) => {
    let flatPage = null;
    // Strip leading slash from path.
    path = path.replace(/^\/+/, "");
    await axios
      // the "extra" slashes around `path` are currently needed to
      // match the `url` attribute of the FlatPage model.
      .get(`http://${process.env.DJANGO_HOSTNAME}:${process.env.DJANGO_PORT}/api/flatpages//${path}/`)
      .then((response) => {
        flatPage = response.data;
        notFound = false;
      })
      .catch((error) => {
        if (error.response?.status === 404) {
          notFound = true;
        } else {
          throw error;
        }
      });
    return flatPage;
  };

  // Retrieve the page.
  page = await retrieveFlatPage(path);

  // If the page was not found, attempt to fall back on a redirect.
  if (!page) {
    const redirectPath = await getRedirectPath(path);
    if (redirectPath) {
      page = await retrieveFlatPage(redirectPath);
    }
  }

  return {
    props: {
      page,
    },
    notFound,
    revalidate: 10,
  };
};

export const getStaticPaths: GetStaticPaths = async () => {
  return {
    paths: [],
    fallback: "blocking",
  };
};
