import BigAnchor from "@/components/BigAnchor";
import { SerpModule } from "@/types/modules";
import { Grid } from "@mui/material";
import Link from "next/link";
import { FC } from "react";
import ModuleUnionCard from "./cards/ModuleUnionCard";

export interface TodayInHistoryProps {
  modules: SerpModule[];
}

const TodayInHistory: FC<TodayInHistoryProps> = ({ modules }: TodayInHistoryProps) => {
  return (
    <Grid container spacing={1} justifyContent="center" alignItems="center">
      {modules.length ? (
        modules.map((module, index) => (
          <Grid item key={index}>
            <Link href={module.absoluteUrl} passHref>
              <BigAnchor>
                <ModuleUnionCard module={module} />
              </BigAnchor>
            </Link>
          </Grid>
        ))
      ) : (
        <p>There are no modules associated with this date.</p>
      )}
    </Grid>
  );
};

export default TodayInHistory;
