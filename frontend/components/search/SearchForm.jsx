import YearSelect from "./YearSelect";
import TextField from "./StyledTextField";
import SearchRadioGroup from "./SearchRadioGroup";

import {useRouter} from "next/router";
import {Container, Grid} from "@material-ui/core";
import {useState} from "react";
import {makeStyles} from "@material-ui/styles";
import EntitySelect from "./EntitySelect";

function useFormState(initialState) {
  const [state, setState] = useState(initialState);
  console.log(state);
  return [
    state,
    ({target}) => setState(
      (prevState) => ({...prevState, [target.name]: target.value})
    )
  ];
}

const useStyles = makeStyles({
  root: {
    maxWidth: "230px",
    paddingTop: "20px",
    // marginRight: "12px",
    "& input": {
      backgroundColor: "white"
    },
    "& .MuiTextField-root": {
      backgroundColor: "white"
    }
  }
});

export default function SearchForm() {
  const classes = useStyles();
  const router = useRouter();

  const [state, setState] = useFormState(router.query);

  return (
    <Container className={classes.root}>
      <Grid container spacing={3} direction={"column"}>
        <Grid item xs={12}>
          <TextField label="Query"/>
        </Grid>

        <Grid item xs={12}>
          <SearchRadioGroup label={"Ordering"} state={state} setState={setState}>
            {["Date", "Relevance"]}
          </SearchRadioGroup>
        </Grid>

        <YearSelect label={"Start year"} name={"start_year"} state={state} setState={setState}/>
        <YearSelect label={"End year"} name={"end_year"} state={state} setState={setState}/>

        <Grid item xs={12}>
          <EntitySelect/>
        </Grid>
      </Grid>
    </Container>
  );
}
