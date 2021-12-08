const SEASONS = [
  [null, "-----"],
  ["winter", "Winter"],
  ["spring", "Spring"],
  ["summer", "Summer"],
  ["fall", "Fall"],
];

const TEN_THOUSAND = 10_000;
const ONE_MILLION = 1_000_000;

const SIGNIFICANT_FIGURES = 4;

const APPROXIMATE_PRESENT_YEAR = 2000;

// https://en.wikipedia.org/wiki/Before_Present
const BP_REFERENCE_YEAR = 1950;

const YBP_LOWER_LIMIT = 29_999; // 30000 with rounding error protection

const BCE_THRESHOLD = YBP_LOWER_LIMIT - BP_REFERENCE_YEAR;

// Dates earlier than this are considered to be circa by default
const BCE_CIRCA_FLOOR = TEN_THOUSAND;

// Dates earlier than this are considered to be prehistory
const BCE_PREHISTORY_FLOOR = TEN_THOUSAND;

// Year values larger than this should be expressed in millions/billions
const MILLIFICATION_FLOOR = ONE_MILLION;

// Year values larger than this should be "prettified" with commas
const PRETTIFICATION_FLOOR = TEN_THOUSAND;

const EXPONENT_INVERSION_BASIS = 30; // --> 20 for the Big Bang
const DECIMAL_INVERSION_BASIS = 100_000; // --> 986200 for the Big Bang

type HistoricDateTimeParams = Record<
  "year" | "monthIndex" | "day" | "seasonIsKnown" | "monthIsKnown" | "dayIsKnown" | "milliseconds",
  number | string | boolean
>;

export class HistoricDateTime extends Date {
  ybp_lower_limit = YBP_LOWER_LIMIT;
  bce_threshold = YBP_LOWER_LIMIT - BP_REFERENCE_YEAR;
  significant_figures = SIGNIFICANT_FIGURES;

  constructor({
    year,
    monthIndex = 1,
    day = 1,
    seasonIsKnown = false,
    monthIsKnown = false,
    dayIsKnown = false,
    milliseconds = 0,
  }: HistoricDateTimeParams) {
    super(
      ...([year, monthIndex, day, seasonIsKnown, monthIsKnown, dayIsKnown, milliseconds].map(
        Number
      ) as Parameters<DateConstructor>)
    );
  }

  // get is_circa(): boolean {
  //   if (this.yearBce) {
  //     return this.yearBce >= BCE_CIRCA_FLOOR;
  //   }
  //   return false;
  // }

  get seasonIsKnown(): boolean {
    return this.getHours() != 1;
  }

  get monthIsKnown(): boolean {
    return this.getMinutes() != 1;
  }

  // get useYbp(): boolean { }

  // get yearBce(): number | null { }

  // get yearBp(): number { }
}
