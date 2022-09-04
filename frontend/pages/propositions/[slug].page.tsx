import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import PropositionDetail from "@/components/propositions/PropositionDetail";
import { Proposition } from "@/types/modules";
import { Button, Grid } from "@mui/material";
import { GetStaticPaths, GetStaticProps } from "next";
import { NextSeo } from "next-seo";
import { FC } from "react";

interface PropositionProps {
  proposition: Proposition;
}

/**
 * A page that renders the HTML of a single proposition.
 */
const PropositionDetailPage: FC<PropositionProps> = ({ proposition }: PropositionProps) => {
  return (
    <Layout>
      <NextSeo
        title={proposition.summary}
        canonical={proposition.absoluteUrl}
        description={proposition.summary}
      />
      <Grid
        container
        direction="row"
        justifyContent="space-evenly"
        alignItems="flex-start"
        style={{ margin: "2rem 0" }}
      >
        <Grid item sm={12} md={6} lg={6} xl={4} style={{ margin: "0 3rem" }}>
          <PropositionDetail proposition={proposition} />
        </Grid>
        {proposition.conflictingPropositions && (
          <>
            {(!!proposition.conflictingPropositions.length && (
              <>
                {proposition.conflictingPropositions.map((conflictingProposition) => (
                  <Grid
                    item
                    key={conflictingProposition.slug}
                    sm={12}
                    md={6}
                    lg={6}
                    xl={4}
                    style={{ margin: "0 3rem" }}
                  >
                    <PropositionDetail
                      key={conflictingProposition.slug}
                      proposition={conflictingProposition}
                    />
                  </Grid>
                ))}
              </>
            )) || (
              <Grid item container xs={12} justifyContent="center">
                <Grid item xs={12} sm={6}>
                  <div
                    style={{
                      margin: "2rem",
                      borderTop: "1px solid gray",
                      textAlign: "center",
                      paddingTop: "1.5rem",
                    }}
                  >
                    <p>This proposition is undisputed.</p>
                    <p>
                      <Button variant="contained" disabled>
                        Dispute
                      </Button>
                    </p>
                  </div>
                </Grid>
              </Grid>
            )}
          </>
        )}
      </Grid>
    </Layout>
  );
};
export default PropositionDetailPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let proposition = {};
  let notFound = false;
  const { slug } = params || {};
  await axiosWithoutAuth
    .get(`http://django:8002/api/propositions/${slug}/`)
    .then((response) => {
      proposition = response.data;
    })
    .catch((error) => {
      if (error.response?.status === 404) {
        notFound = true;
      } else {
        throw error;
      }
    });

  return {
    props: {
      proposition,
    },
    notFound,
    revalidate: 10,
  };
};

export const getStaticPaths: GetStaticPaths = async () => {
  return {
    paths: [],
    fallback: "blocking",
  };
};
