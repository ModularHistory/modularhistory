import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import { GetStaticPaths, GetStaticProps } from "next";
import { NextSeo } from "next-seo";
import Error from "next/error";
import { FC } from "react";

interface ErrorPageProps {
  code: number;
  message: string;
}

const ErrorPage: FC<ErrorPageProps> = (props: ErrorPageProps) => {
  return (
    <Layout>
      <NextSeo title={`${props.code}`} noindex />
      <Error statusCode={props.code} title={props.message} />
    </Layout>
  );
};

export default ErrorPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  const { code } = params || {};
  let message = "";
  await axiosWithoutAuth
    .get(`http://django:8002/api/errors/${code}`)
    .then((response) => {
      console.log(response);
    })
    .catch((error) => {
      message = error.response.data.error;
    });
  return {
    props: {
      code,
      message,
    },
    revalidate: 10,
  };
};

export const getStaticPaths: GetStaticPaths = async () => {
  return {
    paths: [],
    fallback: "blocking",
  };
};
