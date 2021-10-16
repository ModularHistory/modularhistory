import PageHeader from "@/components/PageHeader";
import { Container, Divider, Grid, Link, Paper } from "@mui/material";
import React, { FC } from "react";

const AboutModularHistory: FC  = () => {

  return(
    <Container>
      <PageHeader>About Modularhistory</PageHeader>
      <Paper sx={{p: 2, margin: "0 auto", maxWidth: "80vw", flexGrow: 1}}>
        <Grid container spacing = {2}>
          <Grid item xs>
            <p>ModularHistory is a 501(c)(3) nonprofit organization dedicated to helping people learn about and understand the history of our world, our society, and issues of modern sociopolitical discourse.</p>
            <Divider variant = "middle" />
            <p>ModularHistory provide its content for free.</p>
            <p>To support us, <Link href = "/donations" variant = "body2">{' donate now.'}</Link></p>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};
export default AboutModularHistory;