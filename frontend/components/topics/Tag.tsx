import { Topic } from "@/types/models";
import Chip from "@mui/material/Chip";
import { styled } from "@mui/material/styles";
import Link from "next/link";
import { FC } from "react";

const TagChip = styled(Chip)({
  backgroundColor: "rgba(255, 255, 153, 0.8)",
  fontSize: "0.7rem",
});

interface TagProps {
  topic: Topic;
}

const Tag: FC<TagProps> = ({ topic }: TagProps) => {
  return (
    <Link href={topic.absoluteUrl || `/topics/${topic.slug}`}>
      <a>
        <TagChip label={topic.name} size="small" clickable />
      </a>
    </Link>
  );
};

export default Tag;
