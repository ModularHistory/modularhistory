import Layout from "@/components/Layout";
import Container from "@material-ui/core/Container";
import DropIn from "braintree-web-drop-in-react";
import { GetServerSideProps } from "next";
import { useRouter } from "next/router";
import { FC, useEffect, useState } from "react";
import axiosWithoutAuth from "@/axiosWithoutAuth";

interface PullRequestProps {
  clientToken: string;
}

const PullRequest: FC<PullRequestProps> = (props: PullRequestProps) => {
  const [clientToken, setClientToken] = useState(props.clientToken);
  const [instance, setInstance] = useState(null);
  const router = useRouter();
  return (
    <Layout title="Pull request">
      <Container>
        {(!clientToken && <p className="lead">Loading...</p>) || (
          <div>
            <header>
              <p className="h3">Help us keep ModularHistory running</p>
              <p>
                ModularHistory provide its content for free. If you would like to help keep
                ModularHistory afloat, you can use this form to make a donation.
              </p>
            </header>
            <div className="row col-12 p-0 m-0 mt-3">
              <div className="col pl-0">
                <input
                  type="text"
                  className="form-control"
                  name="name"
                  id="name"
                  placeholder="Name"
                  required
                />
              </div>
              <div className="col pr-0">
                <input
                  type="number"
                  className="form-control"
                  name="amount"
                  id="amount"
                  placeholder="Amount"
                  required
                />
              </div>
            </div>
            <DropIn options={{ authorization: clientToken }} onInstance={(_) => setInstance(_)} />
            <button onClick={makeDonation}>Make donation</button>
          </div>
        )}
      </Container>
    </Layout>
  );
};

export default PullRequest;

export const getServerSideProps: GetServerSideProps = async () => {
  let clientToken = null;
  await axiosWithoutAuth
    .get("http://django:8000/api/donations/token/")
    .then((response) => {
      clientToken = response.data;
    })
    .catch((error) => {
      console.error(error);
    });
  return {
    props: {
      clientToken,
    },
  };
};
