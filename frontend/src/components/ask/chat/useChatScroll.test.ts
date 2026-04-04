import { render, act } from "@testing-library/react";
import React from "react";
import type { Message } from "ai/react";
import { useChatScroll } from "./useChatScroll";

const mockScrollIntoView = jest.fn();

beforeEach(() => {
  mockScrollIntoView.mockClear();
  window.HTMLElement.prototype.scrollIntoView = mockScrollIntoView;
});

function makeMessages(count: number): Message[] {
  return Array.from({ length: count }, (_, i) => ({
    id: `msg-${i}`,
    role: "user" as const,
    content: `message ${i}`,
  }));
}

function TestComponent({ messages }: { messages: Message[] }) {
  const ref = useChatScroll(messages);
  return React.createElement("div", { ref });
}

describe("useChatScroll", () => {
  it("ref を返すこと", () => {
    const { container } = render(
      React.createElement(TestComponent, { messages: [] })
    );
    expect(container.querySelector("div")).toBeTruthy();
  });

  it("メッセージが追加されると scrollIntoView が呼ばれること", () => {
    const { rerender } = render(
      React.createElement(TestComponent, { messages: makeMessages(1) })
    );
    act(() => {
      rerender(React.createElement(TestComponent, { messages: makeMessages(2) }));
    });
    expect(mockScrollIntoView).toHaveBeenCalledWith({ behavior: "smooth" });
  });
});
