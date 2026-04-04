import { render, screen, fireEvent } from "@testing-library/react";
import ChatInput from "./ChatInput";

jest.mock("./useAutoResize", () => ({
  useAutoResize: () => ({ current: null }),
}));

jest.mock("react-dropzone", () => ({
  useDropzone: () => ({
    getRootProps: () => ({}),
    getInputProps: () => ({}),
    isDragActive: false,
    open: jest.fn(),
  }),
}));

const defaultProps = {
  input: "",
  handleInputChange: jest.fn(),
  handleSubmit: jest.fn(),
  isLoading: false,
};

describe("ChatInput", () => {
  it("textarea と送信ボタンが表示されること", () => {
    render(<ChatInput {...defaultProps} />);
    expect(screen.getByPlaceholderText("質問を入力 (Cmd+Enter で送信)")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /ファイルをアップロード/ })).toBeInTheDocument();
  });

  it("isLoading=true のとき textarea が disabled になること", () => {
    render(<ChatInput {...defaultProps} isLoading={true} />);
    expect(screen.getByPlaceholderText("質問を入力 (Cmd+Enter で送信)")).toBeDisabled();
  });

  it("input が空のとき送信ボタンが disabled になること", () => {
    render(<ChatInput {...defaultProps} input="" />);
    const buttons = screen.getAllByRole("button");
    const submitButton = buttons[buttons.length - 1];
    expect(submitButton).toBeDisabled();
  });

  it("input に値があるとき送信ボタンが有効になること", () => {
    render(<ChatInput {...defaultProps} input="質問テキスト" />);
    const buttons = screen.getAllByRole("button");
    const submitButton = buttons[buttons.length - 1];
    expect(submitButton).not.toBeDisabled();
  });

  it("textarea の変更で handleInputChange が呼ばれること", () => {
    const handleInputChange = jest.fn();
    render(<ChatInput {...defaultProps} handleInputChange={handleInputChange} />);
    fireEvent.change(screen.getByPlaceholderText("質問を入力 (Cmd+Enter で送信)"), { target: { value: "新しい入力" } });
    expect(handleInputChange).toHaveBeenCalled();
  });
});
