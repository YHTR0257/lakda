import { render, act } from "@testing-library/react";
import React from "react";
import { useAutoResize } from "./useAutoResize";

function TestTextarea({ value }: { value: string }) {
  const ref = useAutoResize(value);
  return React.createElement("textarea", { ref });
}

describe("useAutoResize", () => {
  afterEach(() => jest.restoreAllMocks());

  function mockComputedStyle(lineHeight: number) {
    jest.spyOn(window, "getComputedStyle").mockReturnValue({
      lineHeight: `${lineHeight}px`,
      paddingTop: "0px",
      paddingBottom: "0px",
    } as CSSStyleDeclaration);
  }

  it("scrollHeight が2行以内なら overflowY が hidden になること", () => {
    mockComputedStyle(20);
    // scrollHeight(20) <= maxHeight(40): hidden
    Object.defineProperty(HTMLTextAreaElement.prototype, "scrollHeight", {
      get: () => 20,
      configurable: true,
    });

    const { container } = render(React.createElement(TestTextarea, { value: "hello" }));
    const textarea = container.querySelector("textarea")!;
    expect(textarea.style.overflowY).toBe("hidden");
  });

  it("scrollHeight が2行を超えたら overflowY が auto になること", () => {
    mockComputedStyle(20);
    // scrollHeight(70) > maxHeight(40): auto
    Object.defineProperty(HTMLTextAreaElement.prototype, "scrollHeight", {
      get: () => 70,
      configurable: true,
    });

    const { container } = render(
      React.createElement(TestTextarea, { value: "line1\nline2\nline3" })
    );
    const textarea = container.querySelector("textarea")!;
    expect(textarea.style.overflowY).toBe("auto");
  });

  it("value が変わると再計算されること", () => {
    mockComputedStyle(20);
    let fakeScrollHeight = 20;
    Object.defineProperty(HTMLTextAreaElement.prototype, "scrollHeight", {
      get: () => fakeScrollHeight,
      configurable: true,
    });

    const { container, rerender } = render(
      React.createElement(TestTextarea, { value: "hello" })
    );
    const textarea = container.querySelector("textarea")!;
    expect(textarea.style.overflowY).toBe("hidden");

    fakeScrollHeight = 70;
    act(() => {
      rerender(React.createElement(TestTextarea, { value: "line1\nline2\nline3" }));
    });
    expect(textarea.style.overflowY).toBe("auto");
  });
});
