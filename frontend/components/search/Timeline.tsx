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
import React, {
  ComponentProps,
  Dispatch,
  FC,
  MutableRefObject,
  RefObject,
  SetStateAction,
  useEffect,
  useRef,
  useState,
} from "react";

type ElementRef<T extends HTMLElement = HTMLElement> = MutableRefObject<T | null>;

const Slider: FC<SliderProps<"span", { componentsProps?: { mark: SliderMarkProps } }>> = styled(
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

interface SliderMarkProps extends ComponentProps<typeof MuiSliderMark> {
  modules: SerpModule[];
  moduleRefs: RefObject<any>[];
  viewStateRegistry: Map<string, Dispatch<SetStateAction<boolean>>>;
}

const SliderMark: FC<SliderMarkProps> = React.memo(
  function SliderMark({ modules, moduleRefs, viewStateRegistry, ...markProps }) {
    // Mui passes this prop but doesn't type it.
    const moduleIndex = (markProps as typeof markProps & { "data-index": number })["data-index"];
    const isBreak = moduleIndex >= modules.length;
    const module = isBreak ? undefined : modules[moduleIndex];

    const [tooltipOpen, setTooltipOpen] = useState(false);
    const [inView, setInView] = useState(false);
    if (module) viewStateRegistry.set(module.absoluteUrl, setInView);

    const handleClick = () => {
      const moduleCard = moduleRefs[moduleIndex].current;
      moduleCard?.scrollIntoView({ behavior: "smooth" });
      moduleCard?.click();
    };

    const sliderMark = (
      <MuiSliderMark {...markProps}>
        {isBreak ? (
          <BreakIcon />
        ) : (
          <Box position={"relative"} bottom={"3px"} padding={"5px"} onClick={handleClick} />
        )}
      </MuiSliderMark>
    );
    return isBreak ? (
      sliderMark
    ) : (
      <Tooltip
        title={
          <Box whiteSpace={"nowrap"} onClick={handleClick}>
            {modules[moduleIndex].title}
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
        {sliderMark}
      </Tooltip>
    );
  },
  (prevProps, nextProps) => {
    const keys: Array<keyof SliderMarkProps> = ["modules", "moduleRefs", "viewStateRegistry"];
    for (const key of keys) {
      if (prevProps[key] !== nextProps[key]) return false;
    }
    return true;
  }
);

export type TimelineProps = {
  modules: SerpModule[];
  moduleRefs: RefObject<any>[];
} & Pick<SliderMarkProps, "viewStateRegistry">;

type TimelineCalculations = {
  now: number;
  scale: (n: number) => number;
  descale: (n: number) => number;
} & Required<Pick<SliderProps, "marks" | "min" | "max">>;

const Timeline: FC<TimelineProps> = ({ modules, moduleRefs, viewStateRegistry }) => {
  const [calculations, setCalculations] = useState<TimelineCalculations | null>(null);
  useEffect(() => {
    const now = new Date().getFullYear();
    const marks: Mark[] = [];
    const years = modules
      .map((m) => m.timelinePosition)
      .filter((n) => !Number.isNaN(n))
      .sort((a, b) => a - b);
    modules.forEach((module, index) =>
      marks.push({
        // add a tiny incremental value to eliminate duplicate keys
        value: module.timelinePosition + Number(`${index}e-5`),
      })
    );

    const ranges = years.slice(0, -1).map((year, index) => years[index + 1] - year);

    const averageDistance = (years[years.length - 1] - years[0]) / years.length;
    const breaks: (Mark & { length: number })[] = [];

    ranges.forEach((rangeLength, index) => {
      if (rangeLength > averageDistance) {
        const [start, end] = years.slice(index, index + 2).map(Math.round);
        const length = end - start;
        const buffer = Math.round(Math.min(averageDistance / 4, length * 0.1));
        // if (length <= buffer * 3) return;

        const break_ = {
          value: start + buffer,
          label: (
            <Box color={"lightgray"}>
              {formatYbp(end - buffer, now)} — {formatYbp(start + buffer, now)}
            </Box>
          ),
          length: length - 2 * buffer,
        };
        breaks.push(break_);
        // we scale marks but don't scale breaks, so create a new object
        marks.push({ ...break_ });
      }
    }, [] as number[]);
    breaks.sort((a, b) => a.value - b.value);
    const reverseBreaks = [...breaks].reverse();

    const scale = (n: number) => {
      for (const { value, length } of reverseBreaks) {
        if (n > value) n -= length;
      }
      return n;
    };

    const descale = (n: number) => {
      for (const { value, length } of breaks) {
        if (n > value) n += length;
      }
      return n;
    };

    marks.forEach((mark) => {
      mark.value = scale(mark.value);
    });

    const buffer = averageDistance / 4;
    const min = Math.floor(years[0] - buffer);
    const max = scale(Math.ceil(years[years.length - 1] + buffer));

    setCalculations({ now, marks, min, max, scale, descale });
  }, [modules]);

  const thumbRefs: ElementRef[] = [useRef(null), useRef(null)];

  if (calculations === null) {
    return <Slider key={0} orientation={"vertical"} defaultValue={[0, 100]} disabled />;
  }

  const { now, marks, min, max, descale } = calculations;

  return (
    <Slider
      key={1}
      onMouseDownCapture={(event) => {
        if (!thumbRefs.map((r) => r.current).includes(event.target as HTMLElement))
          event.stopPropagation();
      }}
      orientation={"vertical"}
      valueLabelDisplay={"on"}
      marks={marks}
      defaultValue={[min, max]}
      min={min}
      max={max}
      valueLabelFormat={(ybp) => formatYbp(descale(ybp), now)}
      componentsProps={{ mark: { modules, moduleRefs, viewStateRegistry } }}
      components={{
        Mark: SliderMark,
        Thumb: (props) => <SliderThumb {...props} ref={thumbRefs[props["data-index"]]} />,
      }}
    />
  );
};

export default Timeline;

const commaRegex = new RegExp(/(\d)(?=(\d{3})+$)/g);

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
  } else if (bce <= 1e4) {
    year = bce;
    type = "BCE";
  } else {
    year = ybp;
    type = "YBP";
  }
  if (type != "CE") {
    if (year >= TEN_THOUSAND) {
      const digits = Math.floor(Math.log10(year)) + 1;
      const divisor = 10 ** (digits - 3);
      year = Math.round(year / divisor) * divisor;
    }

    if (year >= BILLION) {
      year /= BILLION;
      multiplier = "B";
    } else if (year >= MILLION) {
      year /= MILLION;
      multiplier = "M";
    }
  }
  const yearStr = multiplier ? year.toPrecision(3) : year.toString().replace(commaRegex, "$1,");
  return `${yearStr}${multiplier} ${type}`;
}
