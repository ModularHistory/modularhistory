import { PullRequest } from "@/interfaces";
import { CmsPage } from "@/pages/cms";
import { Container, Table, TableBody, TableCell, TableRow } from "@material-ui/core";
import axios from "axios";
import { GetServerSideProps } from "next";
import { Session } from "next-auth";
import { getSession } from "next-auth/client";
import Link from "next/link";
import { FC } from "react";

interface PullRequestsPageProps {
  session: Session;
  pullRequests?: PullRequest[];
}

const PullRequestsPage: FC<PullRequestsPageProps> = (props: PullRequestsPageProps) => {
  return (
    <CmsPage title="Pull requests" activeTab={2} session={props.session}>
      <Container>
        {(!!props.pullRequests?.length && (
          <Table>
            <TableBody>
              {props.pullRequests.map((pullRequest) => (
                <TableRow key={pullRequest.url}>
                  <TableCell>
                    #{pullRequest.number}:{" "}
                    <Link href={`/moderation/reviews/${pullRequest.number}`}>
                      {pullRequest.title}
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )) || <p style={{ textAlign: "center" }}>There are no open pull requests.</p>}
      </Container>
    </CmsPage>
  );
};

export default PullRequestsPage;

export const getServerSideProps: GetServerSideProps = async (context) => {
  const session: Session = await getSession(context);
  if (!session?.accessToken) {
    return {
      props: {
        session,
      },
    };
  }
  let pullRequests = [];
  await axios
    .get("http://django:8000/api/moderation/reviews/", {
      params: context.query,
      headers: {
        Authorization: `Bearer ${session.accessToken}`,
      },
    })
    .then((response) => {
      pullRequests = response.data.results;
    })
    .catch((error) => {
      // TODO...
      console.log(error);
    });
  return {
    props: {
      pullRequests,
      session,
    },
  };
};
