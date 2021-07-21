import Layout from "@/components/Layout";
import { Container } from "@material-ui/core";
import Grid from "@material-ui/core/Grid";
import { GetServerSideProps } from "next";
import { User } from "next-auth";
import { getSession, useSession } from "next-auth/client";
import React, { FC } from "react";
import Image from "react-bootstrap/Image";

interface UserProps {
  user?: User;
}

const UserDetailPage: FC<UserProps> = ({ user }: UserProps) => {
  const [_session, _loading] = useSession();
  return (
    <Layout title={String(user.name || user.username)}>
      <Container style={{ paddingTop: "2rem" }}>
        <Grid container spacing={3} alignContent="center">
          <Grid item sm={4}>
            <div className="profile-img">
              <Image
                src={String(user.avatar || "/profile_pic_placeholder.png")}
                className="rounded-circle z-depth-0"
                alt={`profile image for ${user.name || user.username}`}
                width="200"
                height="200"
              />
            </div>
          </Grid>
          <Grid container item sm={8}>
            <Grid item xs={12}>
              <div className="profile-head">
                <h5>{user.name}</h5>
              </div>
            </Grid>
            <Grid item xs={12}>
              <div>
                <label>Username</label>
              </div>
              <p>{user.username}</p>
            </Grid>
            {user.name && (
              <Grid item xs={12}>
                <div>
                  <label>Name</label>
                </div>
                <div>
                  <p>{user.name}</p>
                </div>
              </Grid>
            )}
            <Grid item xs={12}>
              <div>
                <label>Email</label>
              </div>
              <div>
                <p>{user.email}</p>
              </div>
            </Grid>
          </Grid>
        </Grid>
      </Container>
    </Layout>
  );
};
export default UserDetailPage;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  const session = await getSession(context);
  return {
    props: {
      user: session.user,
    },
  };
};
