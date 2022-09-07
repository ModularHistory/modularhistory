import { SerpModule } from "@/types/modules";
import Compress from "@mui/icons-material/Compress";
import { Box, SliderProps, styled, Tooltip } from "@mui/material";
import { SliderMark as MuiSliderMark } from "@mui/material/Slider";
import { SystemProps } from "@mui/system";
import {
  ComponentProps,
  Dispatch,
  FC,
  memo,
  MouseEventHandler,
  ReactElement,
  ReactNode,
  RefObject,
  SetStateAction,
  useState,
} from "react";
import { observe } from "react-intersection-observer";

const BreakIcon = styled(Compress)({
  transform: "translate(-25%, -50%)",
  color: "gray",
  backgroundColor: "white",
});

export type TimelineMarkModule<T extends HTMLElement = HTMLElement> = Required<
  Pick<SerpModule, "timelinePosition" | "title" | "absoluteUrl">
> & { ref: RefObject<T> };

export type Mark<T extends HTMLElement = HTMLElement> = Exclude<
  SliderProps["marks"],
  boolean | undefined
>[number] &
  (
    | { isBreak: false; module: TimelineMarkModule<T> }
    | { isBreak: true; labelNode: ReactElement; module?: never }
  ) & {
    ref?: HTMLSpanElement;
  };

export type TimelineMarkProps = ComponentProps<typeof MuiSliderMark> & {
  viewStateRegistry: Map<string, Dispatch<SetStateAction<boolean>>>;
  marks: Mark[];
};

const TimelineMark: FC<TimelineMarkProps> = memo(
  function TimelineMark({ marks, viewStateRegistry, ...muiMarkProps }) {
    // Mui passes this prop but doesn't type it.
    const mark = marks[((muiMarkProps as unknown) as { "data-index": number })["data-index"]];
    return mark.isBreak ? (
      <TimelineBreakMark
        mark={mark}
        viewStateRegistry={viewStateRegistry}
        muiMarkProps={muiMarkProps}
      />
    ) : (
      <TimelineModuleMark
        mark={mark}
        viewStateRegistry={viewStateRegistry}
        muiMarkProps={muiMarkProps}
      />
    );
  },
  (prevProps, nextProps) => {
    const keys: Array<keyof TimelineMarkProps> = ["marks", "viewStateRegistry"];
    for (const key of keys) {
      if (prevProps[key] !== nextProps[key]) return false;
    }
    return true;
  }
);

export default TimelineMark;

const TimelineModuleMark: FC<
  Pick<TimelineMarkBaseProps, "viewStateRegistry" | "muiMarkProps"> & {
    mark: Mark & { isBreak: false };
  }
> = ({ mark, viewStateRegistry, muiMarkProps }) => (
  <TimelineMarkBase
    tooltipTitle={mark.module.title}
    markBoxProps={{
      position: "relative",
      bottom: "3px",
      padding: "5px",
    }}
    onClick={() => {
      const moduleCard = mark.module.ref.current;
      if (moduleCard) {
        // click on card once scrolled into view
        moduleCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
        const destroy = observe(
          moduleCard,
          (inView) => {
            if (inView) {
              moduleCard.click();
              destroy();
            }
          },
          { threshold: 1 }
        );
        // some events (like double-click) might create extra observers,
        // so we delete any that weren't triggered in time
        setTimeout(destroy, 2e3);
      }
    }}
    registryKey={mark.module.absoluteUrl}
    mark={mark}
    viewStateRegistry={viewStateRegistry}
    muiMarkProps={muiMarkProps}
    testId={"timelineModuleMark"}
  />
);

const TimelineBreakMark: FC<
  Pick<TimelineMarkBaseProps, "viewStateRegistry" | "muiMarkProps"> & {
    mark: Mark & { isBreak: true };
  }
> = ({ mark, viewStateRegistry, muiMarkProps }) => (
  <TimelineMarkBase
    tooltipTitle={mark.labelNode}
    tooltipStyles={{ zIndex: 1 }}
    markBoxProps={{ children: <BreakIcon /> }}
    registryKey={String(mark.value)}
    mark={mark}
    viewStateRegistry={viewStateRegistry}
    muiMarkProps={muiMarkProps}
    testId={"timelineBreakMark"}
  />
);

interface TimelineMarkBaseProps {
  tooltipTitle: ReactNode;
  tooltipStyles?: SystemProps;
  markBoxProps: ComponentProps<typeof Box>;
  onClick?: MouseEventHandler;
  registryKey: string;
  mark: Mark;
  viewStateRegistry: Map<string, Dispatch<SetStateAction<boolean>>>;
  muiMarkProps: ComponentProps<typeof MuiSliderMark>;
  testId: string;
}

const TimelineMarkBase: FC<TimelineMarkBaseProps> = ({
  tooltipTitle,
  tooltipStyles,
  markBoxProps,
  onClick,
  registryKey,
  mark,
  viewStateRegistry,
  muiMarkProps,
  testId,
}) => {
  const [tooltipOpen, setTooltipOpen] = useState(false);
  const [inView, setInView] = useState(
    // mark.isBreak ? false : isElementInViewport(mark.module.ref.current)
    false
  );

  viewStateRegistry.set(registryKey, setInView);
  return (
    <Tooltip
      title={
        <Box
          whiteSpace={"nowrap"}
          textOverflow={"ellipsis"}
          overflow={"hidden"}
          data-testid={"timelineTooltip"}
        >
          {tooltipTitle}
        </Box>
      }
      arrow
      placement={"right"}
      open={inView || tooltipOpen}
      onOpen={() => setTooltipOpen(true)}
      onClose={() => setTooltipOpen(false)}
      // MUI mis-types "popper" key as PopperProps instead of Partial<PopperProps>
      componentsProps={{
        popper: { disablePortal: true } as any,
        tooltip: { onClick, sx: tooltipStyles },
      }}
    >
      <MuiSliderMark {...muiMarkProps} data-testid={testId}>
        <Box
          ref={(ref: HTMLSpanElement) => {
            mark.ref = ref;
          }}
          onClick={onClick}
          {...markBoxProps}
        />
      </MuiSliderMark>
    </Tooltip>
  );
};

function isElementInViewport(el: HTMLElement | null) {
  if (el === null) return false;
  const { top, bottom, left, right } = el.getBoundingClientRect();
  return (
    top < (window.innerHeight || document.documentElement.clientHeight) &&
    bottom > 0 &&
    left < (window.innerWidth || document.documentElement.clientWidth) &&
    right > 0
  );
}
