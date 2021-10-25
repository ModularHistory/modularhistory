import Layout from "@/components/Layout";
import Error from "next/error";
import { FC } from "react";

const NotFound: FC = () => {
  // Do not record an exception in Sentry for 404. (This is opinionated.)
  return (
    <Layout>
      <Error statusCode={404} />
    </Layout>
  );
};

export default NotFound;
