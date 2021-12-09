import BigAnchor from "@/components/BigAnchor";
import { SerpModule } from "@/types/models";
import { Grid } from "@mui/material";
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
            <BigAnchor href={module.absoluteUrl}>
              <ModuleUnionCard module={module} />
            </BigAnchor>
          </Grid>
        ))
      ) : (
        <p>There are no modules associated with this date.</p>
      )}
    </Grid>
  );
};

export default TodayInHistory;
