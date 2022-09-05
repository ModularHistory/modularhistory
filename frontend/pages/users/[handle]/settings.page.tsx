import { makeDjangoApiUrl } from "@/auth";
import axiosWithoutAuth from "@/axiosWithoutAuth";
import PasswordChangeForm from "@/components/account/PasswordChangeForm";
import ProfileForm from "@/components/account/ProfileForm";
import SocialAccountList from "@/components/account/SocialAccountList";
import Layout from "@/components/Layout";
import { Container, useTheme } from "@mui/material";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Typography from "@mui/material/Typography";
import { AxiosResponse } from "axios";
import { GetServerSideProps } from "next";
import { User } from "next-auth";
import { Provider } from "next-auth/providers";
import { getCsrfToken, getProviders, getSession, useSession } from "next-auth/react";
import { NextSeo } from "next-seo";
import { ChangeEvent, FC, ReactNode, useState } from "react";
import Image from "react-bootstrap/Image";

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
  user: User;
  csrfToken: string;
  providers: Record<string, Provider>;
  socialAccounts: any;
}

const UserSettingsPage: FC<UserSettingsPageProps> = ({
  user,
  csrfToken,
  providers,
  socialAccounts,
}: UserSettingsPageProps) => {
  const theme = useTheme();
  const { data: session } = useSession();
  const [value, setValue] = useState(0);
  const handleChange = (event: ChangeEvent<unknown>, newValue: number) => {
    setValue(newValue);
  };
  if (session) {
    return (
      <Layout>
        <NextSeo title={String(user.name || user.handle)} noindex />
        <Container
          sx={{
            paddingTop: "2rem",
          }}
        >
          <Grid container spacing={3} alignContent="center">
            <Grid item sm={4}>
              <div className="profile-img">
                <Image
                  src={String(user.avatar || "/static/profile_pic_placeholder.png")}
                  className="rounded-circle z-depth-0"
                  alt={`profile image for ${user.name || user.handle}`}
                  width="200"
                  height="200"
                />
              </div>
            </Grid>
            <Grid container item sm={8}>
              <Paper
                sx={{
                  flexGrow: 1,
                }}
              >
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
  if (!session?.user) {
    return {
      redirect: {
        destination: "/",
        permanent: false,
      },
    };
  }
  const _providers = await getProviders();
  const _csrfToken = await getCsrfToken(context);
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
      console.error(
        "Failed to retrieve social accounts:",
        error.response?.data ? error.response.data : error
      );
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
