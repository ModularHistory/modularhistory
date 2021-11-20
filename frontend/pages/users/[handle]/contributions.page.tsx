import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import { Container } from "@mui/material";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import { GetServerSideProps } from "next";
import { User } from "next-auth";
import { getSession, useSession } from "next-auth/client";
import React, { FC } from "react";
import Image from "react-bootstrap/Image";

interface UserContributionsPageProps {
  user?: User;
  usercontributions: any;
}

const UserContributionsPage: FC<UserContributionsPageProps> = ({
  user,
  usercontributions,
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
  let usercontributions = null;
  if (!session?.user) {
    return {
      redirect: {
        destination: "/",
        permanent: false,
      },
    };
  }
  await axiosWithoutAuth
    .get("http://django:8000/api/moderation/contributions/")
    .then((response) => {
      usercontributions = response.data;
    })
    .catch((error) => {
      console.error(error);
    });
  return {
    props: {
      usercontributions,
      user: session?.user ?? null,
    },
  };
};
