import Error from "next/error";
import { FC } from "react";

const NotFound: FC = () => {
  // Do not record an exception in Sentry for 404. (This is opinionated.)
  return <Error statusCode={404} />;
};

export default NotFound;
