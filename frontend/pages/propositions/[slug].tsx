import axiosWithoutAuth from "@/axiosWithoutAuth";
import Layout from "@/components/Layout";
import PropositionDetail from "@/components/propositions/PropositionDetail";
import IssueModal from "@/components/scm/IssueModal";
import { Proposition } from "@/interfaces";
import { Button, Grid } from "@material-ui/core";
import EditIcon from "@material-ui/icons/Edit";
import { GetStaticPaths, GetStaticProps } from "next";
import { useSession } from "next-auth/client";
import { FC, useState } from "react";

interface PropositionProps {
  proposition: Proposition;
}

/**
 * A page that renders the HTML of a single proposition.
 */
const PropositionDetailPage: FC<PropositionProps> = ({ proposition }: PropositionProps) => {
  const [session, _loading] = useSession();
  const [issueModalOpen, setIssueModalOpen] = useState(false);
  const openIssueModal = () => {
    setIssueModalOpen(true);
  };
  const closeIssueModal = () => {
    setIssueModalOpen(false);
  };
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
          <a
            href={`https://github.com/ModularHistory/content/tree/main/propositions/${proposition.id}.toml`}
            rel="noreferrer"
            target="_blank"
          >
            <EditIcon style={{ float: "right", margin: "1rem" }} />
          </a>
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
        {(!!proposition.pullRequests?.length && (
          <div>
            {proposition.pullRequests.map((pullRequest) => (
              <p key={pullRequest.url}>{pullRequest.url}</p>
            ))}
          </div>
        )) ||
          (session?.user?.["isSuperuser"] && (
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
                  <p>No issues have been reported for this module.</p>
                  <p>
                    <Button variant="contained" onClick={openIssueModal}>
                      Report an issue
                    </Button>
                    <IssueModal open={issueModalOpen} />
                  </p>
                </div>
              </Grid>
            </Grid>
          ))}
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
  // await axiosWithoutAuth.get(`http://django:8000/api/cms/propositions/${proposition.id}/`)
  //   .then((response) => {
  //     proposition.cms = response.data;
  //     console.log('CMS: ', proposition.cms);
  //   })
  //   .catch(() => {
  //     proposition.cms = null;
  //   });
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
