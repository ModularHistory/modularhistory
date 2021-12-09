import { Topic } from "@/types/models";
import { FC } from "react";
import Tag from "./Tag";

interface TagListProps {
  topics: Topic[];
}

const TagList: FC<TagListProps> = ({ topics }: TagListProps) => {
  return (
    <ul className="tags">
      {topics.map((topic) => (
        <li key={topic.name} style={{ display: "inline", margin: "2px", listStyle: "none" }}>
          <Tag topic={topic} />
        </li>
      ))}
    </ul>
  );
};

export default TagList;
