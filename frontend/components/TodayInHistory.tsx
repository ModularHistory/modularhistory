import { ModuleUnion, Topic } from "@/types/modules";
import { Grid } from "@mui/material";
import Link from "next/link";
import { FC } from "react";
import ModuleUnionCard from "./cards/ModuleUnionCard";

export interface TodayInHistoryProps {
  todayinhistoryData: Exclude<ModuleUnion, Topic>[];
}

const TodayInHistory: FC<TodayInHistoryProps> = ({ todayinhistoryData }: TodayInHistoryProps) => {
  const items = todayinhistoryData || [];
  return (
    <Grid container spacing={1} justifyContent="center" alignItems="center">
      <>
        {items.length ? (
          items.map((module, index) => (
            <Grid item key={index}>
              <Link href={module.absoluteUrl}>
                <a>
                  <ModuleUnionCard module={module} />
                </a>
              </Link>
            </Grid>
          ))
        ) : (
          <p>There are no modules associated with this date.</p>
        )}
      </>
    </Grid>
  );
};

export default TodayInHistory;
