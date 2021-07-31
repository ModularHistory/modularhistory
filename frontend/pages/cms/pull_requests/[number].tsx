import axiosWithAuth from "@/axiosWithAuth";
import Layout from "@/components/Layout";
import PageHeader from "@/components/PageHeader";
import { PullRequest } from "@/interfaces";
import { Grid } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import { GetServerSideProps } from "next";
import { Session } from "next-auth";
import { getSession, signIn } from "next-auth/client";
import { useRouter } from "next/router";
import { FC } from "react";

interface PullRequestPageProps {
  pullRequest?: PullRequest;
  session: Session;
}

const PullRequestPage: FC<PullRequestPageProps> = (props: PullRequestPageProps) => {
  const { pullRequest, session } = props;
  const router = useRouter();
  const baseUrl = typeof window !== "undefined" ? window.location.origin : "";
  if (!session?.user) {
    if (!session?.user?.email) {
      // TODO: properly prompt user to login instead of doing it automatically
      signIn("github", { callbackUrl: `${baseUrl}/${router.asPath}` });
    }
    return null;
  }
  return (
    <Layout title={`Pull request #${pullRequest.number}`}>
      <Container>
        <PageHeader>
          Pull request {pullRequest.number}: {pullRequest.title}
        </PageHeader>
        <Grid container direction="row" justifyContent="space-evenly" alignItems="flex-start">
          <Grid item sm={12} md={6} lg={6} xl={6} style={{ margin: "0 3rem" }}>
            <p>
              From {pullRequest.sourceBranch.name} to {pullRequest.targetBranch.name}
            </p>
          </Grid>
        </Grid>
      </Container>
    </Layout>
  );
};

export default PullRequestPage;

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { number } = context.params;
  const session = await getSession(context);
  if (!session?.user) {
    return {
      props: {
        session,
      },
    };
  }
  let pullRequest = null;
  await axiosWithAuth
    .get(`http://django:8000/api/cms/pull_requests/${number}/`, {
      headers: {
        Authorization: `Bearer ${session.accessToken}`,
      },
    })
    .then((response) => {
      pullRequest = response.data;
    })
    .catch((error) => {
      console.error("Failed to retrieve pull request:", error);
    });
  return {
    props: {
      pullRequest,
      session,
    },
  };
};
