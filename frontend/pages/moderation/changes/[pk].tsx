import axiosWithAuth from "@/axiosWithAuth";
import PageHeader from "@/components/PageHeader";
import { Change } from "@/interfaces";
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
  const title = change ? `Change #${change.id}` : "eek";
  return (
    <CmsPage title={title} session={session} activeTab={2}>
      {session?.user && change && (
        <Container>
          <PageHeader>Change {change.id}</PageHeader>
          <Grid container direction="row" justifyContent="space-evenly" alignItems="flex-start">
            <Grid item sm={12} md={6} lg={6} xl={6} style={{ margin: "0 3rem" }}>
              <p>{change.changedObject}</p>
            </Grid>
          </Grid>
        </Container>
      )}
    </CmsPage>
  );
};

export default ChangePage;

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { pk } = context.params;
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
    .get(`http://django:8000/api/moderation/changes/${pk}/`, {
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
