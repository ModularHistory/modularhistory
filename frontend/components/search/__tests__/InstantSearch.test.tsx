import { act, render, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import InstantSearch, { InstantSearchProps } from "../InstantSearch/InstantSearch";

describe("Instant search input field", () => {
  const [idKey, labelKey] = ["id", "label"];
  const createOptions = (n = 0) => {
    return [...Array(n).keys()].map((n) => ({ [idKey]: `${n}`, [labelKey]: `label${n}` }));
  };

  const renderInstantSearch = (props?: Partial<InstantSearchProps>) =>
    waitFor(() =>
      render(
        <InstantSearch
          label={""}
          getDataForInput={() => []}
          defaultValue={[]}
          idKey={idKey}
          labelKey={labelKey}
          onChange={() => {
            return;
          }}
          {...props}
        />
      )
    );

  it("works with Promises for defaultValue", async () => {
    const options = createOptions(1);
    const { getAllByText } = await renderInstantSearch({
      defaultValue: Promise.resolve(options),
    });
    expect(getAllByText(options[0][labelKey])).toHaveLength(1);
  });

  it("works with non-Promises for defaultValue", async () => {
    const options = createOptions(1);
    const { getAllByText } = await renderInstantSearch({
      defaultValue: options,
    });
    expect(getAllByText(options[0][labelKey])).toHaveLength(1);
  });

  it("works with non-array for defaultValue", async () => {
    // this behavior is needed because the defaultValue
    // pulled from `router` might not be an array
    const options = createOptions(1);
    const { getAllByText } = await renderInstantSearch({
      defaultValue: options[0],
    });

    expect(getAllByText(options[0][labelKey])).toHaveLength(1);
  });

  it("calls onChange with array of ids", async () => {
    const options = createOptions(2);
    const onChangeMock = jest.fn();
    const { getByTestId, findByText } = await renderInstantSearch({
      onChange: onChangeMock,
      getDataForInput: () => options,
    });

    expect(onChangeMock).toHaveBeenCalledTimes(0);

    // select first option
    userEvent.type(getByTestId("instantSearchInput"), " ");
    await act(async () => {
      userEvent.click(await findByText(options[0][labelKey]));
    });
    expect(onChangeMock).toHaveBeenCalledTimes(1);
    expect(onChangeMock).toHaveBeenLastCalledWith([options[0][idKey]]);

    // select second option
    userEvent.type(getByTestId("instantSearchInput"), " ");
    await act(async () => {
      userEvent.click(await findByText(options[1][labelKey]));
    });
    expect(onChangeMock).toHaveBeenCalledTimes(2);
    expect(onChangeMock).toHaveBeenLastCalledWith(options.map((o) => o[idKey]));
  });

  it("includes defaultValue in onChange arguments", async () => {
    const options = createOptions(2);
    const onChangeMock = jest.fn();
    const { getByTestId, findByText } = await renderInstantSearch({
      onChange: onChangeMock,
      defaultValue: options.slice(0, 1),
      getDataForInput: () => options.slice(1),
    });

    userEvent.type(getByTestId("instantSearchInput"), " ");
    await act(async () => {
      userEvent.click(await findByText(options[1][labelKey]));
    });

    expect(onChangeMock).toBeCalledTimes(1);
    expect(onChangeMock).toBeCalledWith(options.map((o) => o[idKey]));
  });

  it("throttles data fetching", async () => {
    jest.useFakeTimers();

    const getDataForInputMock = jest.fn();
    const throttleDelay = 500;
    getDataForInputMock.mockReturnValue([]);
    const { getByTestId } = await renderInstantSearch({
      getDataForInput: getDataForInputMock,
      throttleDelay,
    });

    const input = getByTestId("instantSearchInput");

    expect(getDataForInputMock).toHaveBeenCalledTimes(0);
    await act(async () => await userEvent.type(input, "watch"));
    expect(getDataForInputMock).toHaveBeenCalledTimes(1);
    await act(async () => await userEvent.type(input, "more"));
    expect(getDataForInputMock).toHaveBeenCalledTimes(1);
    await act(async () => await userEvent.type(input, "anime"));
    expect(getDataForInputMock).toHaveBeenCalledTimes(1);

    jest.advanceTimersByTime(throttleDelay + 1);
    expect(getDataForInputMock).toHaveBeenCalledTimes(2);

    jest.useRealTimers();
  });

  it("doesn't retrieve data for input length below threshold", async () => {
    const minimumSearchLength = 2;
    const options = createOptions(1);
    const getDataForInputMock = jest.fn();
    getDataForInputMock.mockReturnValue(options);
    const { getByTestId, getByText, queryByText } = await renderInstantSearch({
      getDataForInput: getDataForInputMock,
      minimumSearchLength,
    });

    const input = getByTestId("instantSearchInput");
    await act(async () => await userEvent.type(input, "{space}"));
    expect(getDataForInputMock).toHaveBeenCalledTimes(0);
    await act(async () => await userEvent.type(input, "{space}"));
    expect(getDataForInputMock).toHaveBeenCalledTimes(1);
    expect(getDataForInputMock).toHaveBeenCalledWith("  ", expect.anything());
    await act(async () => await userEvent.type(input, "{backspace}"));
    expect(getDataForInputMock).toHaveBeenCalledTimes(1);
    expect(queryByText(options[0][labelKey])).toBeNull();
    getByText("Type to search");
  });
});
