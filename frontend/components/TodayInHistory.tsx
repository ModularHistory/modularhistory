import { Grid } from "@mui/material";
import Link from "next/link";
import { TodayInHistoryProps } from "pages/index.page";
import { FC } from "react";
import ModuleUnionCard from "./cards/ModuleUnionCard";

const TodayInHistory: FC<TodayInHistoryProps> = ({ todayinhistoryData }: TodayInHistoryProps) => {
  const items = todayinhistoryData["results"] || [];
  const abc = "----- TIH COMPONENT DATA---------";
  console.log(abc);
  console.log(todayinhistoryData);
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
