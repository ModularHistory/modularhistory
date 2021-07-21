import PasswordChangeForm from "@/components/account/PasswordChangeForm";
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
import { GetServerSideProps } from "next";
import { User } from "next-auth";
import { csrfToken, getSession, providers, useSession } from "next-auth/client";
import { Provider } from "next-auth/providers";
import { ChangeEvent, FC, ReactNode, useState } from "react";
import Image from "react-bootstrap/Image";
import SwipeableViews from "react-swipeable-views";

interface UserSettingsPageProps {
  user?: User;
  csrfToken: string;
  providers: Provider[];
}

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

const UserSettingsPage: FC<UserSettingsPageProps> = ({
  user,
  csrfToken,
  providers,
}: UserSettingsPageProps) => {
  const classes = useStyles();
  const theme = useTheme();
  const [_session, _loading] = useSession();
  const [value, setValue] = useState(0);
  const handleChange = (event: ChangeEvent<unknown>, newValue: number) => {
    setValue(newValue);
  };
  const handleChangeIndex = (index: number) => {
    setValue(index);
  };
  return (
    <Layout title={String(user.name || user.username)}>
      <Container className={classes.root}>
        <Grid container spacing={3} alignContent="center">
          <Grid item sm={4}>
            <div className="profile-img">
              <Image
                src={String(user.avatar || "/profile_pic_placeholder.png")}
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
              <SwipeableViews
                axis={theme.direction === "rtl" ? "x-reverse" : "x"}
                index={value}
                onChangeIndex={handleChangeIndex}
              >
                <TabPanel value={value} index={0} dir={theme.direction}>
                  <Grid item xs={12}>
                    <div className="profile-head">
                      <h5>{user.name}</h5>
                    </div>
                  </Grid>
                  <Grid item xs={12}>
                    <div>
                      <label>Username</label>
                    </div>
                    <p>{user.username}</p>
                  </Grid>
                  {user.name && (
                    <Grid item xs={12}>
                      <div>
                        <label>Name</label>
                      </div>
                      <div>
                        <p>{user.name}</p>
                      </div>
                    </Grid>
                  )}
                  <Grid item xs={12}>
                    <div>
                      <label>Email</label>
                    </div>
                    <div>
                      <p>{user.email}</p>
                    </div>
                  </Grid>
                </TabPanel>
                <TabPanel value={value} index={1} dir={theme.direction}>
                  <PasswordChangeForm csrfToken={csrfToken} />
                </TabPanel>
                <TabPanel value={value} index={2} dir={theme.direction}>
                  <SocialAccountList providers={providers} />
                </TabPanel>
              </SwipeableViews>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Layout>
  );
};
export default UserSettingsPage;

// https://nextjs.org/docs/basic-features/data-fetching#getserversideprops-server-side-rendering
export const getServerSideProps: GetServerSideProps = async (context) => {
  const session = await getSession(context);
  const _csrfToken = await csrfToken(context);
  return {
    props: {
      user: session.user,
      providers: await providers(),
      csrfToken: _csrfToken,
    },
  };
};
