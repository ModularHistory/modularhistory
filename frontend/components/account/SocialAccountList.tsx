import { Provider } from "next-auth/providers";
import { FC } from "react";

interface SocialAccountListProps {
  providers: Provider[];
}

const SocialAccountList: FC<SocialAccountListProps> = ({ providers }: SocialAccountListProps) => {
  if (!providers.length) {
    return <p className="text-center">You have no linked accounts.</p>;
  }
  return (
    <div>
      {providers.map((provider) => (
        <p key={provider.id}>{provider.name}</p>
      ))}
    </div>
  );
};

export default SocialAccountList;
