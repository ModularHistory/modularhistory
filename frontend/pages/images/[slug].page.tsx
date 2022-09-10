import axiosWithoutAuth from "@/axiosWithoutAuth";
import ModuleContainer from "@/components/details/ModuleContainer";
import ModuleDetail from "@/components/details/ModuleDetail";
import Layout from "@/components/Layout";
import { Image } from "@/types/modules";
import { GetStaticPaths, GetStaticProps } from "next";
import { NextSeo } from "next-seo";
import { FC } from "react";

interface ImageProps {
  image: Image;
}

/**
 * A page that renders the HTML of a single image.
 */
const ImageDetailPage: FC<ImageProps> = ({ image }: ImageProps) => {
  return (
    <Layout>
      <NextSeo
        title={image.captionHtml}
        canonical={image.absoluteUrl}
        description={image.captionHtml}
      />
      <ModuleContainer>
        <ModuleDetail module={image} />
      </ModuleContainer>
    </Layout>
  );
};
export default ImageDetailPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let image;
  let notFound;
  const { slug } = params || {};
  const body = {
    query: `{
      image(slug: "${slug}") {
        slug
        srcUrl
        captionHtml
        providerString
        description
        width
        height
        model
        adminUrl
      }
    }`,
  };
  await axiosWithoutAuth
    .post(`http://${process.env.DJANGO_HOST}:${process.env.DJANGO_PORT}/graphql/`, body)
    .then(({ data }) => {
      image = data.data.image;
    })
    .catch((error) => {
      if (error.response?.status === 404) {
        notFound = true;
      } else {
        throw error;
      }
    });

  return {
    props: {
      image,
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
