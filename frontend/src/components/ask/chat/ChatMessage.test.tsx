import { render, screen } from "@testing-library/react";
import ChatMessage from "./ChatMessage";
import type { Message } from "ai/react";

jest.mock("react-markdown", () => ({
  __esModule: true,
  default: ({ children }: { children: string }) => <div data-testid="markdown">{children}</div>,
}));
jest.mock("remark-gfm", () => ({ __esModule: true, default: () => {} }));
jest.mock("rehype-sanitize", () => ({ __esModule: true, default: () => {} }));
jest.mock("rehype-highlight", () => ({ __esModule: true, default: () => {} }));

const userMessage: Message = {
  id: "1",
  role: "user",
  content: "テスト質問です",
};

const assistantMessage: Message = {
  id: "2",
  role: "assistant",
  content: "テスト回答です",
};

const assistantWithSources: Message = {
  id: "3",
  role: "assistant",
  content: "ソース付き回答",
  data: [{ sources: [{ file: "doc-001", snippet: "スニペット", score: 0.9 }] }] as unknown as JSONValue[],
};

describe("ChatMessage", () => {
  it("ユーザーメッセージのテキストを表示すること", () => {
    render(<ChatMessage message={userMessage} />);
    expect(screen.getByText("テスト質問です")).toBeInTheDocument();
  });

  it("アシスタントメッセージを ReactMarkdown でレンダリングすること", () => {
    render(<ChatMessage message={assistantMessage} />);
    expect(screen.getByTestId("markdown")).toBeInTheDocument();
    expect(screen.getByText("テスト回答です")).toBeInTheDocument();
  });

  it("ストリーミング中はソースを表示しないこと", () => {
    render(<ChatMessage message={assistantWithSources} isStreaming={true} />);
    expect(screen.queryByText("参照ソース (1件)")).not.toBeInTheDocument();
  });

  it("ストリーミング完了後にソースを表示すること", () => {
    render(<ChatMessage message={assistantWithSources} isStreaming={false} />);
    expect(screen.getByText("参照ソース (1件)")).toBeInTheDocument();
  });
});
