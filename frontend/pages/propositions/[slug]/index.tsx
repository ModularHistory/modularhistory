import axiosWithoutAuth from "@/axiosWithoutAuth";
import CmsBlock from "@/components/cms/CmsBlock";
import Layout from "@/components/Layout";
import PropositionDetail from "@/components/propositions/PropositionDetail";
import { Proposition } from "@/interfaces";
import { Button, Grid } from "@material-ui/core";
import { GetStaticPaths, GetStaticProps } from "next";
import { useSession } from "next-auth/client";
import { FC } from "react";

interface PropositionProps {
  proposition: Proposition;
}

/**
 * A page that renders the HTML of a single proposition.
 */
const PropositionDetailPage: FC<PropositionProps> = ({ proposition }: PropositionProps) => {
  const [session, _loading] = useSession();
  return (
    <Layout title={proposition.summary}>
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
        <CmsBlock module={proposition} />
      </Grid>
    </Layout>
  );
};
export default PropositionDetailPage;

export const getStaticProps: GetStaticProps = async ({ params }) => {
  let proposition: Proposition;
  const { slug } = params;
  const body = {
    query: `{
      proposition(slug: "${slug}") {
        id
        absoluteUrl
        summary
        elaboration
        model
        adminUrl
        certainty
        arguments {
          pk
          type
          explanation
          premises {
            absoluteUrl
            dateString
            certainty
            slug
            summary
            elaboration
          }
        }
        conflictingPropositions {
          slug
          absoluteUrl
          summary
          certainty
        }
        pullRequests {
          url
        }
      }
    }`,
  };
  await axiosWithoutAuth
    .post("http://django:8000/graphql/", body)
    .then((response) => {
      proposition = response.data.data.proposition;
    })
    .catch(() => {
      proposition = null;
    });

  if (!proposition) {
    // https://nextjs.org/blog/next-10#notfound-support
    return {
      notFound: true,
    };
  }
  return {
    props: {
      proposition,
    },
    revalidate: 10,
  };
};

export const getStaticPaths: GetStaticPaths = async () => {
  return {
    paths: [],
    fallback: "blocking",
  };
};
