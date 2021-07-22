import { makeDjangoApiUrl } from "@/auth";
import axiosWithoutAuth from "@/axiosWithoutAuth";
import PasswordChangeForm from "@/components/account/PasswordChangeForm";
import ProfileForm from "@/components/account/ProfileForm";
import SocialAccountList from "@/components/account/SocialAccountList";
import Layout from "@/components/Layout";
import { Container, useTheme } from "@material-ui/core";
import Box from "@material-ui/core/Box";
import Grid from "@material-ui/core/Grid";
import Paper from "@material-ui/core/Paper";
import Tab from "@material-ui/core/Tab";
import Tabs from "@material-ui/core/Tabs";
import Typography from "@material-ui/core/Typography";
import { makeStyles } from "@material-ui/styles";
import { AxiosResponse } from "axios";
import { GetServerSideProps } from "next";
import { User } from "next-auth";
import { csrfToken, getSession, providers, useSession } from "next-auth/client";
import { Provider } from "next-auth/providers";
import { ChangeEvent, FC, ReactNode, useState } from "react";
import Image from "react-bootstrap/Image";

const useStyles = makeStyles({
  root: {
    paddingTop: "2rem",
  },
  tabs: {
    flexGrow: 1,
  },
});

interface TabPanelProps {
  children?: ReactNode;
  dir?: string;
  index: any;
  value: any;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`full-width-tabpanel-${index}`}
      aria-labelledby={`full-width-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box p={3}>
          <Typography>{children}</Typography>
        </Box>
      )}
    </div>
  );
}

interface UserSettingsPageProps {
  user?: User;
  csrfToken: string;
  providers: Provider[];
  socialAccounts: any;
}

const UserSettingsPage: FC<UserSettingsPageProps> = ({
  user,
  csrfToken,
  providers,
  socialAccounts,
}: UserSettingsPageProps) => {
  const classes = useStyles();
  const theme = useTheme();
  const [session, _loading] = useSession();
  const [value, setValue] = useState(0);
  const handleChange = (event: ChangeEvent<unknown>, newValue: number) => {
    setValue(newValue);
  };
  if (session) {
    return (
      <Layout title={String(user.name || user.username)}>
        <Container className={classes.root}>
          <Grid container spacing={3} alignContent="center">
            <Grid item sm={4}>
              <div className="profile-img">
                <Image
                  src={String(user.avatar || "/static/profile_pic_placeholder.png")}
                  className="rounded-circle z-depth-0"
                  alt={`profile image for ${user.name || user.username}`}
                  width="200"
                  height="200"
                />
              </div>
            </Grid>
            <Grid container item sm={8}>
              <Paper className={classes.tabs}>
                <Tabs
                  value={value}
                  onChange={handleChange}
                  indicatorColor="primary"
                  textColor="primary"
                  centered
                >
                  <Tab label="Profile" />
                  <Tab label="Password" />
                  <Tab label="Linked accounts" />
                </Tabs>
                <div>
                  <TabPanel value={value} index={0} dir={theme.direction}>
                    <ProfileForm user={user} csrfToken={csrfToken} />
                  </TabPanel>
                  <TabPanel value={value} index={1} dir={theme.direction}>
                    <PasswordChangeForm csrfToken={csrfToken} />
                  </TabPanel>
                  <TabPanel value={value} index={2} dir={theme.direction}>
                    <SocialAccountList providers={providers} accounts={socialAccounts} />
                  </TabPanel>
                </div>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Layout>
    );
  } else {
    return null;
  }
};
export default UserSettingsPage;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  const session = await getSession(context);
  if (!session) {
    return {
      redirect: {
        destination: "/",
        permanent: false,
      },
    };
  }
  const _providers = await providers();
  const _csrfToken = await csrfToken(context);
  let socialAccounts = null;
  await axiosWithoutAuth
    .get(makeDjangoApiUrl("/users/me/social-accounts/"), {
      headers: {
        Authorization: `Bearer ${session.accessToken}`,
      },
    })
    .then(function (response: AxiosResponse) {
      socialAccounts = response.data.results;
    })
    .catch(function (error) {
      if (error.response?.data) {
        console.error(error.response.data);
      }
      console.error(error);
    });
  return {
    props: {
      user: session.user,
      providers: _providers,
      csrfToken: _csrfToken,
      socialAccounts: socialAccounts,
    },
  };
};
