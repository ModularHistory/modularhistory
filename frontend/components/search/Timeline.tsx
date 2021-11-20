import { SerpModule } from "@/types/modules";
import Compress from "@mui/icons-material/Compress";
import {
  Box,
  Slider as MuiSlider,
  sliderClasses,
  SliderMark as MuiSliderMark,
  SliderProps,
  SliderThumb,
  styled,
  Tooltip,
} from "@mui/material";
import {
  ComponentProps,
  Dispatch,
  FC,
  forwardRef,
  memo,
  ReactElement,
  RefObject,
  SetStateAction,
  TouchEventHandler,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { throttle } from "throttle-debounce";

const Slider: FC<SliderProps<"span", { componentsProps?: { mark: TimelineMarkProps } }>> = styled(
  MuiSlider
)({
  height: "77vh",
  [`& .${sliderClasses.mark}`]: {
    width: "12px",
    backgroundColor: "#212529",
  },
  [`.${sliderClasses.thumb}[data-index='0'] .${sliderClasses.valueLabel}`]: {
    top: 58,
    "&:before": { top: -8 },
  },
});

const BreakIcon = styled(Compress)({
  transform: "translate(-25%, -50%)",
  color: "gray",
  backgroundColor: "white",
});

type PositionedModule<T extends Partial<SerpModule>> = T & Required<Pick<T, "timelinePosition">>;

function positionedModuleTypeGuard<T extends Partial<SerpModule>>(
  module: T
): module is PositionedModule<T> {
  return module.timelinePosition != null;
}

type TimelineMarkModule<T extends HTMLElement = HTMLElement> = Required<
  Pick<SerpModule, "timelinePosition" | "title" | "absoluteUrl">
> & { ref: RefObject<T> };

interface TimelineMarkProps extends ComponentProps<typeof MuiSliderMark> {
  viewStateRegistry: Map<string, Dispatch<SetStateAction<boolean>>>;
  marks: Mark[];
}

const TimelineMark: FC<TimelineMarkProps> = memo(
  function TimelineMark({ viewStateRegistry, marks, ...markProps }) {
    // Mui passes this prop but doesn't type it.
    const index = (markProps as typeof markProps & { "data-index": number })["data-index"];
    const mark = marks[index];

    const [tooltipOpen, setTooltipOpen] = useState(false);
    const [inView, setInView] = useState(
      mark.isBreak ? false : isElementInViewport(mark.module.ref.current)
    );

    if (mark.isBreak) {
      viewStateRegistry.set(String(mark.value), setInView);
      return (
        <Tooltip
          title={
            <Box whiteSpace={"nowrap"} data-testid={"timelineTooltip"}>
              {mark.label}
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
            tooltip: { sx: { zIndex: 100 } },
          }}
        >
          <MuiSliderMark {...markProps} data-testid={"timelineBreak"}>
            <Box
              ref={(ref: HTMLSpanElement) => {
                mark.ref = ref;
              }}
            >
              <BreakIcon />
            </Box>
          </MuiSliderMark>
        </Tooltip>
      );
    }

    viewStateRegistry.set(mark.module.absoluteUrl, setInView);

    const handleClick = () => {
      const moduleCard = mark.module.ref.current;
      moduleCard?.scrollIntoView({ behavior: "smooth" });
      moduleCard?.click();
    };

    return (
      <Tooltip
        title={
          <Box whiteSpace={"nowrap"} onClick={handleClick} data-testid={"timelineTooltip"}>
            {mark.module.title}
          </Box>
        }
        arrow
        placement={"right"}
        open={inView || tooltipOpen}
        onOpen={() => setTooltipOpen(true)}
        onClose={() => setTooltipOpen(false)}
        // MUI mis-types "popper" key as PopperProps instead of Partial<PopperProps>
        componentsProps={{ popper: { disablePortal: true } as any }}
      >
        <MuiSliderMark {...markProps} data-testid={"timelineMark"}>
          <Box
            position={"relative"}
            bottom={"3px"}
            padding={"5px"}
            onClick={handleClick}
            ref={(ref: HTMLDivElement) => {
              mark.ref = ref;
            }}
          />
        </MuiSliderMark>
      </Tooltip>
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

interface TimelineThumbProps extends ComponentProps<typeof SliderThumb> {
  refs: HTMLSpanElement[];
  "data-index": number;
}

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

export type TimelineProps<T extends HTMLElement = HTMLElement> = {
  modules: Array<
    Omit<TimelineMarkModule<T>, "timelinePosition"> &
      Partial<Pick<TimelineMarkModule<T>, "timelinePosition">>
  >;
} & Pick<TimelineMarkProps, "viewStateRegistry"> &
  Partial<Pick<SliderProps, "sx">>;

type Mark<T extends HTMLElement = HTMLElement> = Exclude<
  SliderProps["marks"],
  boolean | undefined
>[number] &
  (
    | { isBreak: false; module: TimelineMarkModule<T> }
    | { isBreak: true; label: ReactElement; module?: never }
  ) & {
    ref?: HTMLSpanElement;
  };

interface TimelineCalculations extends Required<Pick<SliderProps, "min" | "max">> {
  marks: Mark[];
  now: number;
  scale: (n: number) => number;
  descale: (n: number) => number;
}

const Timeline: FC<TimelineProps> = ({ modules, viewStateRegistry, sx }) => {
  // Some modules will possibly not have dates. Since we rely on the indexes of
  // marks and modules aligning, we must filter out undated modules.
  const datedModules = useMemo(() => modules.filter(positionedModuleTypeGuard), [modules]);

  // Performing calculations asynchronously does not improve performance much currently,
  // but will improve both CSR and SSR when `modules.length` increases in the future.
  const [calculations, setCalculations] = useState<TimelineCalculations | null>(null);
  useEffect(() => {
    setCalculations(null);
    if (datedModules.length < 2) return;
    const now = new Date().getFullYear();

    const marks: TimelineCalculations["marks"] = datedModules.map(
      ({ timelinePosition, absoluteUrl, title, ref }, index) => ({
        // add a tiny incremental value to eliminate duplicate keys
        value: timelinePosition + index * 10 ** -5,
        module: {
          timelinePosition,
          absoluteUrl,
          title,
          ref,
        },
        isBreak: false,
      })
    );

    // mark & module indexes must correspond, so we can only sort after creating marks
    const positions = datedModules.map((m) => m.timelinePosition);
    positions.sort((a, b) => a - b);

    // lengths of time between consecutive timeline marks
    const ranges = positions.slice(1).map((position, index) => position - positions[index]);
    // total time spanned by timeline marks
    const totalRange = positions[positions.length - 1] - positions[0];
    const averageRange = totalRange / positions.length;
    // we use this to normalize the slider scale to 1000 points
    // so the thumbs always appear to slide smooooothly
    const baseMultiplier = 1e3 / totalRange;

    const breaks: (Pick<Mark, "value"> & { length: number })[] = [];

    ranges.forEach((rangeLength, index) => {
      if (rangeLength > averageRange) {
        const [start, end] = positions.slice(index, index + 2);
        const buffer = Math.min(averageRange / 4, rangeLength / 10);

        const break_ = {
          value: start + buffer,
          length: rangeLength - 2 * buffer,
        };

        // we scale marks but don't scale breaks, so we track them separately
        breaks.push(break_);
        marks.push({
          value: break_.value,
          label: (
            <Box color={"lightgray"}>
              {formatYbp(end - buffer, now)} — {formatYbp(start + buffer, now)}
            </Box>
          ),
          isBreak: true,
        });
      }
    });

    breaks.sort((a, b) => a.value - b.value);
    const reverseBreaks = [...breaks].reverse();

    // each timeline mark is scaled down by the breaks before it
    const scale = (n: number) => {
      for (const { value, length } of reverseBreaks) {
        if (n > value) n -= length;
      }
      return n * baseMultiplier;
    };

    // we must scale back up to calculate correct labels and input positions
    const descale = (n: number) => {
      n /= baseMultiplier;
      for (const { value, length } of breaks) {
        if (n > value) n += length;
      }
      return n;
    };

    marks.forEach((mark) => {
      mark.value = scale(mark.value);
    });

    const buffer = averageRange / 4;
    const min = scale(Math.floor(positions[0] - buffer));
    const max = scale(Math.ceil(positions[positions.length - 1] + buffer));

    setCalculations({ now, marks, min, max, scale, descale });
    setValue([min, max]);
  }, [datedModules]);

  const thumbRefs = useRef<TimelineThumbProps["refs"]>([]).current;
  const [value, setValue] = useState([0, 100]);
  const handleChange = useCallback((_, value) => setValue(value), []);

  const touchTimeoutRef = useRef<number>();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const handleTouchMove: TouchEventHandler = useCallback(
    throttle(100, true, (event) => {
      clearTimeout(touchTimeoutRef.current);
      const { clientY } = event.touches[0];
      const measuredMarks = marks.map((mark) => {
        const { top } = mark.ref?.getBoundingClientRect() ?? {};
        return { mark, distance: top ? Math.abs(clientY - top) : Number.POSITIVE_INFINITY };
      });
      measuredMarks
        .sort((a, b) => a.distance - b.distance)
        .forEach(({ mark }, sortIndex) => {
          viewStateRegistry.get(mark.module?.absoluteUrl ?? String(mark.value))?.(sortIndex < 5);
        });
    }),
    [calculations]
  );

  const maybeStopPropagation = useCallback(
    (event: Pick<MouseEvent | TouchEvent, "target" | "stopPropagation">) => {
      // by default the slider will move thumbs to click locations anywhere on the rail,
      // so we block clicks that are not directly on the thumbs.
      if (!thumbRefs.includes(event.target as HTMLElement)) {
        event.stopPropagation();
      }
    },
    [thumbRefs]
  );

  const handleTouchStart: TouchEventHandler = useCallback(
    (event) => {
      maybeStopPropagation(event);
      handleTouchMove(event);
    },
    [maybeStopPropagation, handleTouchMove]
  );

  const handleTouchEnd: TouchEventHandler = useCallback(() => {
    touchTimeoutRef.current = window.setTimeout(() => {
      for (const setState of viewStateRegistry.values()) {
        setState(false);
      }
    }, 1e3);
  }, [viewStateRegistry]);

  if (calculations === null) {
    return <Slider orientation={"vertical"} value={[0, 100]} disabled />;
  }

  const { now, marks, min, max, descale } = calculations;

  return (
    <Slider
      onMouseDownCapture={maybeStopPropagation}
      onTouchStartCapture={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      onTouchMove={handleTouchMove}
      orientation={"vertical"}
      valueLabelDisplay={"on"}
      marks={marks}
      onChange={handleChange}
      value={value}
      min={min}
      max={max}
      valueLabelFormat={(ybp) => formatYbp(descale(ybp), now)}
      componentsProps={{
        mark: { viewStateRegistry, marks },
        thumb: { refs: thumbRefs },
      }}
      components={{
        Mark: TimelineMark,
        Thumb: TimelineThumb,
      }}
      sx={sx}
    />
  );
};

export default Timeline;

const commaRegex = new RegExp(/(?!^\d{4}$)(\d)(?=(\d{3})+$)/g);

function formatYbp(ybp: number, thisYear: number) {
  const TEN_THOUSAND = 1e4;
  const MILLION = 1e6;
  const BILLION = 1e9;
  const diff = thisYear - ybp;
  const bce = -diff - 1;

  let year: number;
  let type: "CE" | "BCE" | "YBP";
  let multiplier: "M" | "B" | "" = "";

  if (diff > 0) {
    year = diff;
    type = "CE";
  } else if (bce <= TEN_THOUSAND) {
    year = bce;
    type = "BCE";
  } else {
    year = ybp;
    type = "YBP";
  }

  if (year >= BILLION) {
    year /= BILLION;
    multiplier = "B";
  } else if (year >= MILLION) {
    year /= MILLION;
    multiplier = "M";
  }

  const yearStr = multiplier
    ? year.toPrecision(3)
    : Math.round(year).toString().replace(commaRegex, "$1,");
  return `${yearStr}${multiplier} ${type}`;
}

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
