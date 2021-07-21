import axios from "@/axiosWithAuth";
import { AxiosResponse } from "axios";
import { useSession } from "next-auth/client";
import { Provider } from "next-auth/providers";
import { FC } from "react";
import {
  DiscordLoginButton,
  FacebookLoginButton,
  GithubLoginButton,
  GoogleLoginButton,
  TwitterLoginButton,
} from "react-social-login-buttons";

interface SocialAccountListProps {
  providers: Provider[];
  accounts: any[];
}
const SOCIAL_LOGIN_BUTTONS = {
  facebook: FacebookLoginButton,
  discord: DiscordLoginButton,
  google: GoogleLoginButton,
  twitter: TwitterLoginButton,
  github: GithubLoginButton,
};

interface SocialConnectButtonProps {
  provider: Provider;
}
const SocialConnectButton: FC<SocialConnectButtonProps> = ({
  provider,
}: SocialConnectButtonProps) => {
  const Button = SOCIAL_LOGIN_BUTTONS[provider.id];
  const handleSocialConnect = async (provider_id: string) => {
    await axios
      .post(`/api/users/auth/${provider_id}/connect/`, {})
      .then(function (response: AxiosResponse) {
        console.log(`${response}`);
      })
      .catch(function (error) {
        console.error(error);
      });
  };
  return (
    <Button
      style={{ minWidth: "245px", maxWidth: "245px" }}
      onClick={() => handleSocialConnect(provider.id)}
    >
      Connect {provider.name}
    </Button>
  );
};

const SocialAccountList: FC<SocialAccountListProps> = ({
  providers,
  accounts,
}: SocialAccountListProps) => {
  const [_session, _loading] = useSession();
  return (
    <div>
      {Object.keys(providers).map(
        (provider, index) =>
          providers[provider].name != "Credentials" && (
            <div key={index}>
              <p>{providers[provider].name}</p>
              {(accounts.includes(providers[provider].name) && null) || (
                <SocialConnectButton provider={providers[provider]} />
              )}
            </div>
          )
      )}
      {accounts}
    </div>
  );
};

export default SocialAccountList;
