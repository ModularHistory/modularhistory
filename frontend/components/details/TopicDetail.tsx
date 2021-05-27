import { Topic } from "@/interfaces";
import { FC } from "react";

interface TopicDetailProps {
  topic: Topic;
}

const TopicDetail: FC<TopicDetailProps> = ({ topic }: TopicDetailProps) => {
  return (
    <>
      <h1 className="text-center card-title" dangerouslySetInnerHTML={{ __html: topic.name }} />
      <div dangerouslySetInnerHTML={{ __html: topic.description }} />
    </>
  );
};

export default TopicDetail;
