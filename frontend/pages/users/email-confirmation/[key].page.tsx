import axios from "@/axiosWithAuth";
import Layout from "@/components/Layout";
import { Container } from "@mui/material";
import Grid from "@mui/material/Grid";
import { GetServerSideProps } from "next";
import { NextSeo } from "next-seo";
import React, { FC } from "react";

interface EmailConfirmationPageProps {
  message?: string;
}

const EmailConfirmationPage: FC<EmailConfirmationPageProps> = ({
  message,
}: EmailConfirmationPageProps) => {
  return (
    <Layout>
      <NextSeo title={"Email confirmation"} noindex />
      <Container style={{ paddingTop: "2rem" }}>
        <Grid container spacing={3} alignContent="center">
          <Grid item sm={12}>
            <p>{message}</p>
          </Grid>
        </Grid>
      </Container>
    </Layout>
  );
};
export default EmailConfirmationPage;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  const { key } = context.params || {};
  let message = "Something went wrong.";
  await axios
    .post("/api/users/auth/email-verification/", {
      key,
    })
    .then(function () {
      message = "Email address was verified successfully.";
    })
    .catch(function (error) {
      message = `Failed to verify email address: ${error}`;
    });
  return {
    props: {
      message,
    },
  };
};
