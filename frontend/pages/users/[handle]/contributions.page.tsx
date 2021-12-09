import axiosWithAuth from "@/axiosWithAuth";
import Layout from "@/components/Layout";
import { ContentContribution } from "@/types/models";
import { Card, CardContent, CardHeader, Container, Skeleton } from "@mui/material";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import { GetServerSideProps } from "next";
import { User } from "next-auth";
import { getSession, useSession } from "next-auth/client";
import Link from "next/link";
import React, { FC } from "react";
import Image from "react-bootstrap/Image";

interface UserContributionsPageProps {
  user?: User;
  contentContributions: ContentContribution[];
}

const CONTRIBUTION_GUIDELINES_URL_PATH = "/about/contributions";

const UserContributionsPage: FC<UserContributionsPageProps> = ({
  user,
  contentContributions,
}: UserContributionsPageProps) => {
  const [session, _loading] = useSession();
  if (!user || _loading) return null;
  if (session) {
    return (
      <Layout>
        <Container
          sx={{
            paddingTop: "2rem",
          }}
        >
          <Grid container spacing={3} alignContent="center">
            <Grid item sm={4}>
              <div className="profile-img">
                <Image
                  src={String(user.avatar || "/static/profile_pic_placeholder.png")}
                  className="rounded-circle z-depth-0"
                  alt={`profile image for ${user.name || user.handle}`}
                  width="200"
                  height="200"
                />
              </div>
            </Grid>
            <Grid container item sm={8} textAlign="center">
              <Paper
                sx={{
                  flexGrow: 1,
                  paddingTop: 2,
                }}
              >
                <Typography variant="h6" gutterBottom component="div">
                  {" "}
                  My Contributions{" "}
                </Typography>
                <>
                  {contentContributions.length ? (
                    contentContributions.map((contribution, index) => (
                      <Grid item key={index}>
                        <Link href={contribution.absoluteUrl}>
                          <a>
                            {`#${contribution.id} to ${contribution.change.contentObject.title}`}
                          </a>
                        </Link>
                      </Grid>
                    ))
                  ) : _loading ? (
                    <Grid item>
                      <Card sx={{ minWidth: "15rem" }}>
                        <CardHeader title={"Fetching content"} hidden />
                        <CardContent>
                          <Skeleton sx={{ minHeight: 200, width: "100%" }} />
                        </CardContent>
                      </Card>
                    </Grid>
                  ) : (
                    <div>
                      <p>You have not contributed to any contributions yet.</p>
                      <p>
                        Before making content contributions, please read the{" "}
                        <Link href={CONTRIBUTION_GUIDELINES_URL_PATH}>
                          <a>contribution guidelines</a>
                        </Link>
                        .
                      </p>
                    </div>
                  )}
                </>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Layout>
    );
  } else {
    return null;
  }
};
export default UserContributionsPage;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  const session = await getSession(context);
  let contentContributions: UserContributionsPageProps[] = [];
  if (!session?.user) {
    return {
      redirect: {
        destination: "/",
        permanent: false,
      },
    };
  }
  await axiosWithAuth
    .get("http://django:8000/api/moderation/contributions/", {
      headers: {
        Authorization: `Bearer ${session.accessToken}`,
      },
    })
    .then((response) => {
      contentContributions = response.data;
    })
    .catch((error) => {
      console.error(error);
    });
  return {
    props: {
      contentContributions,
      user: session?.user ?? null,
    },
  };
};
