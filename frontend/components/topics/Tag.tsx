import { Topic } from "@/types/modules";
import Chip from "@material-ui/core/Chip";
import { makeStyles } from "@material-ui/styles";
import Link from "next/link";
import { FC } from "react";

const useStyles = makeStyles({
  tag: {
    backgroundColor: "rgba(255, 255, 153, 0.8)",
    fontSize: "0.7rem",
  },
});

interface TagProps {
  topic: Topic;
}

const Tag: FC<TagProps> = ({ topic }: TagProps) => {
  const classes = useStyles();
  return (
    <Link href={topic.absoluteUrl || `/topics/${topic.slug}`}>
      <a>
        <Chip label={topic.name} className={classes.tag} size="small" clickable />
      </a>
    </Link>
  );
};

export default Tag;
