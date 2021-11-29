import { SerpModule } from "@/types/modules";
import Compress from "@mui/icons-material/Compress";
import {
  Box,
  Mark,
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
  memo,
  MutableRefObject,
  RefObject,
  SetStateAction,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

const Slider: FC<SliderProps<"span", { componentsProps?: { mark: TimelineMarkProps } }>> = styled(
  MuiSlider
)({
  height: "80vh",
  position: "fixed",
  left: "40px",
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
  return !(module.timelinePosition == null);
}

type TimelineMarkModule<T extends HTMLElement> = Required<
  Pick<SerpModule, "timelinePosition" | "title" | "absoluteUrl">
> & { ref: RefObject<T> };

interface TimelineMarkProps<T extends HTMLElement = HTMLElement>
  extends ComponentProps<typeof MuiSliderMark> {
  modules: Array<TimelineMarkModule<T>>;
  viewStateRegistry: Map<string, Dispatch<SetStateAction<boolean>>>;
}

const TimelineMark: FC<TimelineMarkProps> = memo(
  function TimelineMark({ modules, viewStateRegistry, ...markProps }) {
    // Mui passes this prop but doesn't type it.
    const moduleIndex = (markProps as typeof markProps & { "data-index": number })["data-index"];
    const isBreak = moduleIndex >= modules.length;
    const module = isBreak ? undefined : modules[moduleIndex];

    const [tooltipOpen, setTooltipOpen] = useState(false);
    const [inView, setInView] = useState(module ? isElementInViewport(module.ref.current) : false);

    if (!module) {
      return (
        <MuiSliderMark {...markProps} data-testid={"timelineBreak"}>
          <BreakIcon />
        </MuiSliderMark>
      );
    }

    viewStateRegistry.set(module.absoluteUrl, setInView);

    const handleClick = () => {
      const moduleCard = module.ref.current;
      moduleCard?.scrollIntoView({ behavior: "smooth" });
      moduleCard?.click();
    };

    return (
      <Tooltip
        title={
          <Box whiteSpace={"nowrap"} onClick={handleClick} data-testid={"timelineTooltip"}>
            {module.title}
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
          <Box position={"relative"} bottom={"3px"} padding={"5px"} onClick={handleClick} />
        </MuiSliderMark>
      </Tooltip>
    );
  },
  (prevProps, nextProps) => {
    const keys: Array<keyof TimelineMarkProps> = ["modules", "viewStateRegistry"];
    for (const key of keys) {
      if (prevProps[key] !== nextProps[key]) return false;
    }
    return true;
  }
);

export type TimelineProps<T extends HTMLElement = HTMLElement> = {
  modules: Array<
    Omit<TimelineMarkModule<T>, "timelinePosition"> &
      Partial<Pick<TimelineMarkModule<T>, "timelinePosition">>
  >;
} & Pick<TimelineMarkProps, "viewStateRegistry">;

type TimelineCalculations = {
  now: number;
  scale: (n: number) => number;
  descale: (n: number) => number;
} & Required<Pick<SliderProps, "marks" | "min" | "max">>;

const Timeline: FC<TimelineProps> = ({ modules, viewStateRegistry }) => {
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

    const positions = datedModules.map((m) => m.timelinePosition);
    const marks: Mark[] = positions.map((position, index) => ({
      // add a tiny incremental value to eliminate duplicate keys
      value: position + index * 10 ** -5,
    }));

    // mark & module indexes must correspond, so we can only sort after creating marks
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

  const thumbRefs: MutableRefObject<HTMLElement | null>[] = [useRef(null), useRef(null)];
  const [value, setValue] = useState([0, 100]);
  const handleChange = useCallback((_, value) => setValue(value), []);

  if (calculations === null) {
    return <Slider orientation={"vertical"} value={[0, 100]} disabled />;
  }

  const { now, marks, min, max, descale } = calculations;

  return (
    <Slider
      onMouseDownCapture={(event) => {
        // by default the slider will move thumbs to click locations anywhere on the rail,
        // so we block clicks that are not directly on the thumbs.
        if (!thumbRefs.map((r) => r.current).includes(event.target as HTMLElement))
          event.stopPropagation();
      }}
      orientation={"vertical"}
      valueLabelDisplay={"on"}
      marks={marks}
      onChange={handleChange}
      value={value}
      min={min}
      max={max}
      valueLabelFormat={(ybp) => formatYbp(descale(ybp), now)}
      componentsProps={{
        mark: { modules: datedModules, viewStateRegistry },
        thumb: { disabled: true },
      }}
      components={{
        Mark: TimelineMark,
        Thumb: (props) => <SliderThumb {...props} ref={thumbRefs[props["data-index"]]} />,
      }}
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
