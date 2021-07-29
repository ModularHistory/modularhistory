import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import { Grid } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import { GetServerSideProps } from "next";
import { useSession } from "next-auth/client";
import { useRouter } from "next/router";
import { FC } from "react";

interface PullRequestProps {
  clientToken: string;
}

const PullRequest: FC<PullRequestProps> = (props: PullRequestProps) => {
  const [session, _loading] = useSession();
  const router = useRouter();
  return (
    <Layout title="Create pull request">
      <Container>
        <PageHeader>Create pull request</PageHeader>
        <Grid container direction="row" justifyContent="space-evenly" alignItems="flex-start">
          <Grid item sm={12} md={6} lg={6} xl={6} style={{ margin: "0 3rem" }}>
            Are you sure?
          </Grid>
        </Grid>
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
