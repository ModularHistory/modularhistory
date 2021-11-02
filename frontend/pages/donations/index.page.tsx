import Layout from "@/components/Layout";
import Container from "@mui/material/Container";
import { NextSeo } from "next-seo";
import Link from "next/link";
import React, { FC } from "react";

const introduction = `
  ModularHistory is a non-profit organization that helps people to learn about and
  understand history. Donate to our cause because learning can't wait.
`;

const Donations: FC = () => {
  return (
    <Layout>
      <NextSeo
        title="Donations"
        canonical={"/donations"}
        description={
          "Learn how you can support ModularHistory's educational mission through a small one-time or recurring donation."
        }
      />
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
        <div className="text-center">
          <div className="pt-5">
            <p className="h1">Donate</p>
          </div>
          <div className="pt-5 m-auto col-6">
            <p className="sm w-70">{introduction}</p>
          </div>
          <div className="pt-5 col-4 m-auto row">
            <Link href={"/donations/make"}>
              <a className="col btn btn-primary mr-3" type="button">
                Donate Now &nbsp;<i className="fa fa-dollar-sign"></i>
              </a>
            </Link>{" "}
            <Link href={"/about"}>
              <a className="col btn btn-primary ml-3" type="button">
                About &nbsp;<i className="fa fa-info-circle"></i>
              </a>
            </Link>
          </div>
        </div>
      </Container>
    </Layout>
  );
};

export default Donations;
