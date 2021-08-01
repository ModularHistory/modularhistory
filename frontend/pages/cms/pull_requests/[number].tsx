import axiosWithAuth from "@/axiosWithAuth";
import PageHeader from "@/components/PageHeader";
import { PullRequest } from "@/interfaces";
import { Grid } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import { GetServerSideProps } from "next";
import { Session } from "next-auth";
import { getSession } from "next-auth/client";
import { FC } from "react";
import { CmsPage } from "..";

interface PullRequestPageProps {
  pullRequest?: PullRequest;
  session: Session;
}

const PullRequestPage: FC<PullRequestPageProps> = (props: PullRequestPageProps) => {
  const { pullRequest, session } = props;
  const title = pullRequest ? `Pull request #${pullRequest.number}` : "eek";
  return (
    <CmsPage title={title} session={session} activeTab={2}>
      {session?.user && pullRequest && (
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
      )}
    </CmsPage>
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
      console.log(pullRequest);
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
