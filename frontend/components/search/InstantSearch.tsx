import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import axios, { AxiosRequestConfig } from "axios";
import React, {
  FC,
  SyntheticEvent,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { throttle } from "throttle-debounce";
import { SearchFormContext } from "./SearchForm";

type Option = Record<string, string | number>;

interface InstantSearchProps {
  label: string;
  name: string;
  getDataForInput: (input: string, config: AxiosRequestConfig) => Promise<Option[]>;
  getInitialValue: (ids: (string | number)[]) => Promise<Option[]>;
  labelKey: string;
  idKey?: string;
  minimumSearchLength?: number;
  throttleDelay?: number;
}

/**
 * A TextInput component that instantly retrieves suggested
 * options from ElasticSearch as the user types.
 * @param label - the input field label.
 * @param name - the query parameter name used during form submission.
 * @param getDataForInput - the callback used to retrieve results for a given text input.
 * @param getInitialValue - the callback used to load option data for an array of option IDs.
 * @param labelKey - the key used to access an option's label attribute.
 * @param idKey - the key used to access an option's id attribute.
 * @param minimumSearchLength - the minimum length of text input required to call `getDataForInput`.
 * @param throttleDelay - the delay in ms between calls to `getDataForInput`.
 * @constructor
 */
const InstantSearch: FC<InstantSearchProps> = ({
  label,
  name,
  getDataForInput,
  getInitialValue,
  labelKey,
  idKey = "id",
  minimumSearchLength = 1,
  throttleDelay = 250,
}: InstantSearchProps) => {
  const { formState, setFormState, disabled } = useContext(SearchFormContext);
  const [options, setOptions] = useState<Option[]>([]);
  const [selectedOptions, setSelectedOptions] = useState<Option[]>([]);
  const [inputValue, setInputValue] = useState("");

  // load labels for values initially loaded from url parameters
  useEffect(() => {
    let initialValue = formState[name] || [];
    if (!Array.isArray(initialValue)) {
      initialValue = [initialValue];
    }
    if (initialValue.length === 0) return;

    getInitialValue(initialValue).then((options) => {
      setSelectedOptions((prevState) => [...prevState, ...options]);
    });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleValueChange = (event: SyntheticEvent, values: Option[]) => {
    setFormState((prevState) => ({ ...prevState, [name]: values.map((value) => value[idKey]) }));
    setSelectedOptions(values);
  };

  // Throttling behavior only works if the same instance of
  // the throttled callback is used, so we use `useCallback`.
  // eslint-disable-next-line
  const getThrottledDataForInput = useCallback(
    throttle(throttleDelay, (...args: Parameters<typeof getDataForInput>) =>
      getDataForInput(...args)
        .then(setOptions)
        // TODO: add more resilient error handling
        .catch((error) => {
          if (!axios.isCancel(error)) {
            console.error(error);
          }
        })
    ),
    [getDataForInput]
  );
  const cancelTokenSourceRef = useRef(axios.CancelToken.source());
  const handleInputChange = (event: SyntheticEvent, value: string) => {
    setInputValue(value);

    // when input changes, cancel any pending requests
    cancelTokenSourceRef.current.cancel();
    cancelTokenSourceRef.current = axios.CancelToken.source();

    if (value.length < minimumSearchLength) {
      setOptions([]);
      return;
    }

    getThrottledDataForInput(value, { cancelToken: cancelTokenSourceRef.current.token });
  };

  // https://next.material-ui.com/components/autocomplete/
  return (
    <Autocomplete
      multiple
      limitTags={5}
      noOptionsText={"Type to search"}
      options={[...options, ...selectedOptions]}
      filterOptions={() => options}
      getOptionLabel={(option) => option[labelKey] as string}
      value={selectedOptions}
      onChange={handleValueChange}
      // we do not use strict equality here since ids may be numbers or strings
      isOptionEqualToValue={(option, value) => option[idKey] == value[idKey]}
      inputValue={inputValue}
      onInputChange={handleInputChange}
      ChipProps={{ size: "small" }}
      disabled={disabled}
      renderInput={(params) => <TextField {...params} variant="outlined" label={label} />}
      sx={{
        "& .MuiChip-root": {
          margin: 1,
          fontSize: "11px",
          height: "20px",
          "& .MuiChip-label": {
            paddingLeft: "6px",
            paddingRight: "8px",
          },
          "& .MuiChip-deleteIcon": {
            height: "18px",
            width: "18px",
            marginRight: "2px",
          },
        },
      }}
    />
  );
};

export default InstantSearch;
