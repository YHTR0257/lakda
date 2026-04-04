import { render, screen } from "@testing-library/react";
import SourceList from "./SourceList";
import type { AnswerSource } from "@/types/ask";

const mockSources: AnswerSource[] = [
  { file: "doc-001", snippet: "最初のスニペット", score: 0.95 },
  { file: "doc-002", snippet: "2番目のスニペット", score: 0.72 },
];

describe("SourceList", () => {
  it("sources が空のときは何も表示しないこと", () => {
    const { container } = render(<SourceList sources={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it("ファイル名を表示すること", () => {
    render(<SourceList sources={mockSources} />);
    expect(screen.getByText("doc-001")).toBeInTheDocument();
    expect(screen.getByText("doc-002")).toBeInTheDocument();
  });

  it("スニペットを表示すること", () => {
    render(<SourceList sources={mockSources} />);
    expect(screen.getByText("最初のスニペット")).toBeInTheDocument();
    expect(screen.getByText("2番目のスニペット")).toBeInTheDocument();
  });

  it("スコアをパーセント表示すること", () => {
    render(<SourceList sources={mockSources} />);
    expect(screen.getByText("スコア: 95.0%")).toBeInTheDocument();
    expect(screen.getByText("スコア: 72.0%")).toBeInTheDocument();
  });

  it("件数を表示すること", () => {
    render(<SourceList sources={mockSources} />);
    expect(screen.getByText("参照ソース (2件)")).toBeInTheDocument();
  });
});
