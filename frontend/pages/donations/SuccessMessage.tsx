import Layout from "@/components/Layout";
import Container from "@material-ui/core/Container";
import React from "react";

export default function SuccessMessage() {
  return (
    <Layout title="Success">
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
          <p className="h3">Donated Successfully.</p>
          <p>Thank you for your donation! Your patronage makes ModularHistory possible.</p>
        </header>
      </Container>
    </Layout>
  );
}
