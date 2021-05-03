import { PostulationModule } from "@/interfaces";
import { FC } from "react";

interface PostulationDetailProps {
  postulation: PostulationModule;
}

const PostulationDetail: FC<PostulationDetailProps> = ({ postulation }: PostulationDetailProps) => {
  let titleHtml = postulation["summary"];
  return (
    <>
      <h1 className="text-center card-title" dangerouslySetInnerHTML={{ __html: titleHtml }} />
      <div dangerouslySetInnerHTML={{ __html: postulation["elaboration"] }} />
    </>
  );
};

export default PostulationDetail;
