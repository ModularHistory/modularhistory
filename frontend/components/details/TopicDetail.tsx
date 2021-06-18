import ModuleCard from "@/components/cards/ModuleCard";
import { Topic } from "@/interfaces";
import { FC } from "react";
import HTMLEllipsis from "react-lines-ellipsis/lib/html";

interface TopicDetailProps {
  topic: Topic;
}

const TopicDetail: FC<TopicDetailProps> = ({ topic }: TopicDetailProps) => {
  return (
    <>
      <h1 className="text-center card-title" dangerouslySetInnerHTML={{ __html: topic.name }} />
      <div dangerouslySetInnerHTML={{ __html: topic.description }} />
      <div>
        {topic.propositions.map((proposition) => (
          <ModuleCard key={proposition.slug} module={proposition} header={proposition.summary}>
            <HTMLEllipsis unsafeHTML={proposition.elaboration} maxLine="4" basedOn="words" />
          </ModuleCard>
        ))}
      </div>
    </>
  );
};

export default TopicDetail;
