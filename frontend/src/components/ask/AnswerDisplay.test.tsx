import { render, screen } from "@testing-library/react";
import AnswerDisplay from "./AnswerDisplay";
import type { ConfirmResponse } from "@/types/ask";

const mockAnswer: ConfirmResponse = {
  session_id: "session-001",
  question: "AttributeError の原因は？",
  answer: "AttributeError はオブジェクトに存在しない属性にアクセスしたときに発生します。",
  sources: [
    {
      file: "doc-python-errors.md",
      snippet: "AttributeError の詳細説明...",
      score: 0.95,
    },
    {
      file: "doc-debugging.md",
      snippet: "デバッグ手法の説明...",
      score: 0.82,
    },
  ],
  timestamp: "2026-03-17T00:00:00+00:00",
};

describe("AnswerDisplay", () => {
  it("質問テキストを表示すること", () => {
    render(<AnswerDisplay answer={mockAnswer} answerHtml={null} />);
    expect(screen.getByText("AttributeError の原因は？")).toBeInTheDocument();
  });

  it("answerHtml が null のとき回答テキストをプレーンテキストで表示すること", () => {
    render(<AnswerDisplay answer={mockAnswer} answerHtml={null} />);
    expect(
      screen.getByText(
        "AttributeError はオブジェクトに存在しない属性にアクセスしたときに発生します。"
      )
    ).toBeInTheDocument();
  });

  it("answerHtml が渡されたとき HTML としてレンダリングすること", () => {
    render(
      <AnswerDisplay
        answer={mockAnswer}
        answerHtml="<p>HTMLレンダリングされた回答</p>"
      />
    );
    expect(screen.getByText("HTMLレンダリングされた回答")).toBeInTheDocument();
  });

  it("ソース一覧を表示すること", () => {
    render(<AnswerDisplay answer={mockAnswer} answerHtml={null} />);
    expect(screen.getByText("doc-python-errors.md")).toBeInTheDocument();
    expect(screen.getByText("doc-debugging.md")).toBeInTheDocument();
    expect(screen.getByText("AttributeError の詳細説明...")).toBeInTheDocument();
  });

  it("ソースのスコアをパーセンテージで表示すること", () => {
    render(<AnswerDisplay answer={mockAnswer} answerHtml={null} />);
    expect(screen.getByText("スコア: 95.0%")).toBeInTheDocument();
    expect(screen.getByText("スコア: 82.0%")).toBeInTheDocument();
  });

  it("ソースが0件のとき参照ソースセクションを表示しないこと", () => {
    const answerNoSources: ConfirmResponse = { ...mockAnswer, sources: [] };
    render(<AnswerDisplay answer={answerNoSources} answerHtml={null} />);
    expect(screen.queryByText(/参照ソース/)).not.toBeInTheDocument();
  });

  it("参照ソース件数を表示すること", () => {
    render(<AnswerDisplay answer={mockAnswer} answerHtml={null} />);
    expect(screen.getByText("参照ソース (2件)")).toBeInTheDocument();
  });
});
