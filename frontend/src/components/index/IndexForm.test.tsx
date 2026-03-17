import { render, screen, fireEvent } from "@testing-library/react";
import IndexForm from "./IndexForm";

jest.mock("react", () => ({
  ...jest.requireActual("react"),
  useActionState: (action: unknown, initialState: unknown) => [
    initialState,
    action,
  ],
}));

jest.mock("react-dom", () => ({
  ...jest.requireActual("react-dom"),
  useFormStatus: () => ({ pending: false }),
}));

jest.mock("@/app/index/actions", () => ({
  indexDocument: jest.fn(),
}));

describe("IndexForm", () => {
  it("Document ID フィールドと送信ボタンが表示される", () => {
    render(<IndexForm />);

    expect(screen.getByLabelText("Document ID（任意）")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Run Indexing" })
    ).toBeInTheDocument();
  });

  it("初期状態ではテキスト入力タブが表示される", () => {
    render(<IndexForm />);

    expect(screen.getByRole("button", { name: "テキスト入力" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ファイルアップロード" })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Markdown テキストを入力/)).toBeInTheDocument();
  });

  it("ファイルアップロードタブに切り替えられる", () => {
    render(<IndexForm />);

    fireEvent.click(screen.getByRole("button", { name: "ファイルアップロード" }));

    expect(screen.getByText(/\.md ファイル/)).toBeInTheDocument();
  });

  it("初期状態ではバナーが表示されない", () => {
    render(<IndexForm />);

    expect(screen.queryByText("Indexing complete")).not.toBeInTheDocument();
  });
});
