import { render, screen } from "@testing-library/react";
import ChatWindow from "./ChatWindow";
import type { Message } from "ai/react";

// useChatScroll の scrollIntoView を抑制
beforeEach(() => {
  window.HTMLElement.prototype.scrollIntoView = jest.fn();
});

jest.mock("react-markdown", () => ({
  __esModule: true,
  default: ({ children }: { children: string }) => <div>{children}</div>,
}));
jest.mock("remark-gfm", () => ({ __esModule: true, default: () => {} }));
jest.mock("rehype-sanitize", () => ({ __esModule: true, default: () => {} }));
jest.mock("rehype-highlight", () => ({ __esModule: true, default: () => {} }));

const userMessage: Message = {
  id: "1",
  role: "user",
  content: "テスト質問",
};
const assistantMessage: Message = {
  id: "2",
  role: "assistant",
  content: "テスト回答",
};

describe("ChatWindow", () => {
  it("メッセージが空のときメッセージリストが空であること", () => {
    const { container } = render(<ChatWindow messages={[]} isLoading={false} />);
    expect(container.querySelectorAll(".space-y-4 > *")).toHaveLength(1); // bottomRef のみ
  });

  it("ユーザーメッセージとアシスタントメッセージを表示すること", () => {
    render(<ChatWindow messages={[userMessage, assistantMessage]} isLoading={false} />);
    expect(screen.getByText("テスト質問")).toBeInTheDocument();
    expect(screen.getByText("テスト回答")).toBeInTheDocument();
  });

  it("isLoading=true かつ最後がユーザーメッセージのときタイピングインジケーターを表示すること", () => {
    const { container } = render(
      <ChatWindow messages={[userMessage]} isLoading={true} />
    );
    // アニメーションドット3つ（animate-bounce クラス）を確認
    const dots = container.querySelectorAll(".animate-bounce");
    expect(dots).toHaveLength(3);
  });

  it("isLoading=false のときタイピングインジケーターを表示しないこと", () => {
    const { container } = render(
      <ChatWindow messages={[userMessage]} isLoading={false} />
    );
    const dots = container.querySelectorAll(".animate-bounce");
    expect(dots).toHaveLength(0);
  });
});
