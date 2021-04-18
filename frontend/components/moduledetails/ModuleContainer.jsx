import {Container} from "@material-ui/core";
import ModuleDetail from "@/components/moduledetails/ModuleDetail";

export default function ModuleContainer({module}) {
  return (
    <Container maxWidth={"md"} style={{marginTop: "20px"}}>
      <ModuleDetail module={module}/>
    </Container>
  );
}