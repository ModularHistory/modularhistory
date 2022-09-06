import { SliderThumb } from "@mui/material";
import { ComponentProps, FC, forwardRef } from "react";

export type TimelineThumbProps = ComponentProps<typeof SliderThumb> & {
  refs: HTMLSpanElement[];
  "data-index": number;
};

const TimelineThumb: FC<TimelineThumbProps> = ({ refs, ...props }) => {
  // SliderThumb does forward its ref, but it is mis-typed, so we have to cast it.
  const SliderThumbWithRef = SliderThumb as ReturnType<typeof forwardRef>;
  return (
    <SliderThumbWithRef
      {...props}
      ref={(ref: HTMLSpanElement) => {
        refs[props["data-index"]] = ref;
      }}
      data-testid={"timelineThumb"}
    />
  );
};

export default TimelineThumb;
