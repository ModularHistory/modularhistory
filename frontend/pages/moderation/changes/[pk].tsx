import axiosWithAuth from "@/axiosWithAuth";
import PageHeader from "@/components/PageHeader";
import { Grid } from "@material-ui/core";
import Container from "@material-ui/core/Container";
import { GetServerSideProps } from "next";
import { Session } from "next-auth";
import { getSession } from "next-auth/client";
import { FC } from "react";
import { CmsPage } from "..";

interface ChangePageProps {
  change?: Change;
  session: Session;
}

const ChangePage: FC<ChangePageProps> = (props: ChangePageProps) => {
  const { change, session } = props;
  const title = change ? `Pull request #${change.number}` : "eek";
  return (
    <CmsPage title={title} session={session} activeTab={2}>
      {session?.user && change && (
        <Container>
          <PageHeader>
            Pull request {change.number}: {change.title}
          </PageHeader>
          <Grid container direction="row" justifyContent="space-evenly" alignItems="flex-start">
            <Grid item sm={12} md={6} lg={6} xl={6} style={{ margin: "0 3rem" }}>
              <p>
                From {change.sourceBranch.name} to {change.targetBranch.name}
              </p>
            </Grid>
          </Grid>
        </Container>
      )}
    </CmsPage>
  );
};

export default ChangePage;

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
  let change = null;
  await axiosWithAuth
    .get(`http://django:8000/api/moderation/reviews/${number}/`, {
      headers: {
        Authorization: `Bearer ${session.accessToken}`,
      },
    })
    .then((response) => {
      change = response.data;
      console.log(change);
    })
    .catch((error) => {
      console.error("Failed to retrieve change:", error);
    });
  return {
    props: {
      change,
      session,
    },
  };
};
