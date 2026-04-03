import { render, screen } from "@testing-library/react";
import ChatMessageBubble from "./ChatMessage";
import type { ChatMessage } from "@/store/askStore";

const userMessage: ChatMessage = {
  id: "msg-1",
  role: "user",
  text: "AttributeError の原因は？",
  timestamp: "2026-03-17T00:00:00+00:00",
};

const assistantMessage: ChatMessage = {
  id: "msg-2",
  role: "assistant",
  text: "AttributeError はオブジェクトに存在しない属性にアクセスしたときに発生します。",
  answerHtml: null,
  sources: [
    { file: "doc-python-errors.md", snippet: "詳細説明...", score: 0.95 },
  ],
  timestamp: "2026-03-17T00:00:00+00:00",
};

describe("ChatMessageBubble", () => {
  it("ユーザーメッセージを右揃えで表示すること", () => {
    render(<ChatMessageBubble message={userMessage} />);
    const container = screen.getByTestId("chat-message-user");
    expect(container).toHaveClass("justify-end");
    expect(screen.getByText("AttributeError の原因は？")).toBeInTheDocument();
  });

  it("アシスタントメッセージを左揃えで表示すること", () => {
    render(<ChatMessageBubble message={assistantMessage} />);
    const container = screen.getByTestId("chat-message-assistant");
    expect(container).toHaveClass("justify-start");
  });

  it("answerHtml がある場合 HTML としてレンダリングすること", () => {
    const msg: ChatMessage = {
      ...assistantMessage,
      answerHtml: "<p>HTMLレンダリングされた回答</p>",
    };
    render(<ChatMessageBubble message={msg} />);
    expect(screen.getByText("HTMLレンダリングされた回答")).toBeInTheDocument();
  });

  it("エラーメッセージを表示すること", () => {
    const errorMsg: ChatMessage = {
      id: "msg-err",
      role: "assistant",
      text: "",
      error: "エラーが発生しました。",
      timestamp: "2026-03-17T00:00:00+00:00",
    };
    render(<ChatMessageBubble message={errorMsg} />);
    expect(screen.getByText("エラーが発生しました。")).toBeInTheDocument();
  });

  it("ソース一覧を表示すること", () => {
    render(<ChatMessageBubble message={assistantMessage} />);
    expect(screen.getByText("doc-python-errors.md")).toBeInTheDocument();
    expect(screen.getByText("参照ソース (1件)")).toBeInTheDocument();
  });
});
