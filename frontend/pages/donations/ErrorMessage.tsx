import Layout from "@/components/Layout";
import Container from "@material-ui/core/Container";
import React from "react";

export default function ErrorMessage() {
  return (
    <Layout title={"Error"}>
      <Container
        sx={{
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginTop: "1.5rem",
          marginBottom: "2rem",
        }}
      >
        <header>
          <p className="h3">Oops, something went wrong.</p>
          <p>Sorry, there were some issues with your donation.</p>
        </header>
      </Container>
    </Layout>
  );
}
