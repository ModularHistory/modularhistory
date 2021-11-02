import { Grid } from "@mui/material";
import { signIn } from "next-auth/client";
import React, { FunctionComponent, ReactElement } from "react";
import {
  DiscordLoginButton,
  FacebookLoginButton,
  GithubLoginButton,
  GoogleLoginButton,
  TwitterLoginButton,
} from "react-social-login-buttons";

// https://www.npmjs.com/package/react-social-login-buttons
export const SOCIAL_LOGIN_BUTTONS = {
  facebook: FacebookLoginButton,
  discord: DiscordLoginButton,
  google: GoogleLoginButton,
  twitter: TwitterLoginButton,
  github: GithubLoginButton,
};

const CREDENTIALS_KEY = "credentials";

export interface Provider {
  id: typeof CREDENTIALS_KEY | keyof typeof SOCIAL_LOGIN_BUTTONS;
  name: string;
}

interface SocialLoginProps {
  providers: Provider[];
  callbackUrl: string;
  onError: CallableFunction;
}

const SocialLogin: FunctionComponent<SocialLoginProps> = ({
  providers,
  callbackUrl,
  onError,
}: SocialLoginProps) => {
  const socialAuthLoginComponents: ReactElement[] = [];
  const handleSocialLogin = async (provider_id: string) => {
    try {
      signIn(provider_id, { callbackUrl });
    } catch (error) {
      onError(`${error}`);
    }
  };
  let SocialLoginButton;
  Object.entries(providers).forEach(([, provider]) => {
    if (provider.id === CREDENTIALS_KEY) {
      return null;
    }
    SocialLoginButton = SOCIAL_LOGIN_BUTTONS[provider.id];
    socialAuthLoginComponents.push(
      <SocialLoginButton
        key={provider.name}
        style={{ minWidth: "245px", maxWidth: "245px" }}
        onClick={() => handleSocialLogin(provider.id)}
      >
        Sign in with {provider.name}
      </SocialLoginButton>
    );
  });
  return (
    <div>
      {(!!socialAuthLoginComponents.length && (
        <Grid id="social-sign-in" container justifyContent="center">
          {socialAuthLoginComponents}
        </Grid>
      )) || <p className="text-center">Other sign-in options are unavailable.</p>}
    </div>
  );
};

export default SocialLogin;
