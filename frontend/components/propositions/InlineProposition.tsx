import { Proposition } from "@/interfaces";
import Link from "next/link";
import { FC } from "react";

interface InlinePropositionProps {
  proposition: Proposition;
}

const certaintyColors = ["FFFFFF", "FF0000", "FFFF00", "lightgreen", "00FF00"];

const InlineProposition: FC<InlinePropositionProps> = ({
  proposition,
  ...childProps
}: InlinePropositionProps) => {
  const certaintyColor = proposition.certainty
    ? certaintyColors[proposition.certainty]
    : "lightgray";
  return (
    <span
      {...childProps}
      style={{
        position: "relative",
        display: "inline-block",
        border: `1px solid lightgray`,
        boxShadow: `2px 0 0 1px ${certaintyColor} inset`,
        borderRadius: "5px",
      }}
    >
      {proposition.dateString && (
        <small
          style={{
            position: "absolute",
            top: 0,
            left: "20%",
            transform: "translate(-50% , -50%)",
            zIndex: 1,
            backgroundImage: "linear-gradient(rgba(0,0,0,0), white, rgba(0,0,0,0))",
            padding: "0 0.2rem",
          }}
        >
          {proposition.dateString}
        </small>
      )}
      <span style={{ padding: "5px 7px", display: "inline-block" }}>
        <Link href={proposition.absoluteUrl}>{proposition.summary}</Link>
      </span>
    </span>
  );
};

export default InlineProposition;
