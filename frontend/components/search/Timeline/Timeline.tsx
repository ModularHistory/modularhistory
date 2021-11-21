import { SerpModule } from "@/types/modules";
import { Box, Slider as MuiSlider, sliderClasses, SliderProps, styled } from "@mui/material";
import { FC, TouchEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { throttle } from "throttle-debounce";
import TimelineMark, { Mark, TimelineMarkModule, TimelineMarkProps } from "./TimelineMark";
import TimelineThumb, { TimelineThumbProps } from "./TimelineThumb";

const Slider: FC<SliderProps<"span", { componentsProps?: { mark: TimelineMarkProps } }>> = styled(
  MuiSlider
)({
  // remove margin and add padding to increase mouse/touch event area
  margin: 0,
  marginBottom: 48,
  // MUI media query attempts to override padding on touch devices
  // TODO: investigate how to disable default media query and remove "!important"
  padding: "0 50px !important",
  [`& .${sliderClasses.mark}`]: {
    width: "12px",
    backgroundColor: "#212529",
  },
  [`.${sliderClasses.thumb}[data-index='0'] .${sliderClasses.valueLabel}`]: {
    top: 58,
    "&:before": { top: -8 },
  },
});

type MouseOrTouchEvent = Pick<MouseEvent | TouchEvent, "target" | "stopPropagation"> &
  (
    | (Pick<TouchEvent, "touches"> & { clientY?: never })
    | (Pick<MouseEvent, "clientY"> & { touches?: never })
  );

type PositionedModule<T extends Partial<SerpModule>> = T & Required<Pick<T, "timelinePosition">>;

function positionedModuleTypeGuard<T extends Partial<SerpModule>>(
  module: T
): module is PositionedModule<T> {
  return module.timelinePosition != null;
}

export type TimelineProps<T extends HTMLElement = HTMLElement> = {
  modules: Array<
    Omit<TimelineMarkModule<T>, "timelinePosition"> &
      Partial<Pick<TimelineMarkModule<T>, "timelinePosition">>
  >;
} & Pick<TimelineMarkProps, "viewStateRegistry"> &
  Partial<Pick<SliderProps, "sx">>;

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
    const averageRange = totalRange / (positions.length - 1);
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
          labelNode: (
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
  const handleMouseOrTouchMove = useCallback(
    throttle(100, true, (event: MouseOrTouchEvent) => {
      clearTimeout(touchTimeoutRef.current);
      const { clientY } = event.touches ? event.touches[0] : event;
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
    (event: MouseOrTouchEvent) => {
      // by default the slider will move thumbs to click locations anywhere on the rail,
      // so we block clicks that are not directly on the thumbs.
      if (!thumbRefs.includes(event.target as HTMLElement)) {
        event.stopPropagation();
      }
    },
    [thumbRefs]
  );

  const handleTouchStart = useCallback(
    (event: TouchEvent) => {
      maybeStopPropagation(event);
      handleMouseOrTouchMove(event);
    },
    [maybeStopPropagation, handleMouseOrTouchMove]
  );

  const handleMouseOrTouchEnd = useCallback(() => {
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
      onMouseLeave={handleMouseOrTouchEnd}
      onTouchEnd={handleMouseOrTouchEnd}
      onMouseMove={handleMouseOrTouchMove}
      onTouchMove={handleMouseOrTouchMove}
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
