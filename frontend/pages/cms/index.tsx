import Layout, { LayoutProperties } from "@/components/Layout";
import { Container, Table, TableBody, TableCell, TableRow } from "@material-ui/core";
import Tab from "@material-ui/core/Tab";
import Tabs from "@material-ui/core/Tabs";
import { GetServerSideProps } from "next";
import { Session } from "next-auth";
import { getSession } from "next-auth/client";
import Error from "next/error";
import Link from "next/link";
import { FC } from "react";

interface CmsPageProps extends LayoutProperties {
  activeTab: number;
  session: Session;
}

export const CmsPage: FC<CmsPageProps> = (props: CmsPageProps) => {
  const handleTabChange = (event) => {
    event.preventDefault();
  };
  console.log(props.session.user.name);
  return (
    <Layout title={props.title}>
      {(!props.session?.user && (
        // TODO: make custom error page
        <Error statusCode={401} title={"Not authorized"}>
          Not authorized
        </Error>
      )) || (
        <>
          <div className="text-center" style={{ marginBottom: "2rem" }}>
            <Tabs
              value={props.activeTab}
              onChange={handleTabChange}
              indicatorColor="primary"
              textColor="primary"
              centered
            >
              <Link href={"/moderation"}>
                <a>
                  <Tab label="Content" />
                </a>
              </Link>
              <Link href={"/moderation/issues"}>
                <a>
                  <Tab label="Issues" />
                </a>
              </Link>
              <Link href={"/moderation/reviews"}>
                <a>
                  <Tab label="Modification reviews" />
                </a>
              </Link>
            </Tabs>
          </div>
          {props.children}
        </>
      )}
    </Layout>
  );
};

interface Directory {
  name: string;
  path: string;
}

interface CmsLandingPageProps {
  directories?: Directory[];
  session: Session;
}

const CmsLandingPage: FC<CmsLandingPageProps> = (props: CmsLandingPageProps) => {
  const directories: Directory[] = props.directories ?? [
    { name: "propositions", path: "propositions" },
  ];
  return (
    <CmsPage title="CMS" activeTab={0} session={props.session}>
      <Container>
        <Table>
          <TableBody>
            {directories.map((directory) => (
              <TableRow key={directory.path}>
                <TableCell>
                  <Link href={`/moderation/${directory.path}`}>{directory.name}</Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Container>
    </CmsPage>
  );
};

export default CmsLandingPage;

export const getServerSideProps: GetServerSideProps = async (context) => {
  const session: Session = await getSession(context);
  return {
    props: {
      session,
    },
  };
};
